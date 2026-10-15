"""Exercise real SDK transaction decoration with a read-phase contention fault."""

from unittest.mock import Mock

import pytest
from google.api_core.exceptions import Aborted
from google.cloud.firestore_v1 import Transaction

from app.errors import AppError
from app.storage import FirestoreStore


def firestore_store(reads, *, commit_error=None):
    store = FirestoreStore.__new__(FirestoreStore)
    store.client = Mock()
    reference = store.client.collection.return_value.document.return_value
    reference.get.side_effect = reads
    transactions = []

    def transaction(**kwargs):
        value = Mock(spec=Transaction)
        value._read_only = False
        value._max_attempts = kwargs.get("max_attempts", 5)
        value._id = f"transaction-{len(transactions)}".encode()
        if commit_error:
            value._commit.side_effect = commit_error
        transactions.append(value)
        return value

    store.client.transaction.side_effect = transaction
    return store, reference, transactions


async def test_read_abort_retries_then_reports_conversation_busy():
    snapshot = Mock(exists=True)
    snapshot.to_dict.return_value = {"active": True}
    store, reference, transactions = firestore_store([Aborted("read contention"), snapshot])
    calls = []

    def mutate(docs):
        calls.append(docs)
        if docs[("conversations", "chat")]["active"]:
            raise AppError("Conversation is busy.", 409, "conversation_busy")
        raise AssertionError("The second read must see the committed winner.")

    with pytest.raises(AppError) as error:
        await store.atomic([("conversations", "chat")], mutate)
    assert error.value.code == "conversation_busy"
    assert reference.get.call_count == 2 and len(calls) == 1
    assert len(transactions) == 2
    assert all(transaction._commit.call_count == 0 for transaction in transactions)
    transactions[0]._rollback.assert_called_once()


async def test_read_retry_commits_mutation_only_once():
    snapshot = Mock(exists=False)
    store, reference, transactions = firestore_store([Aborted("read contention"), snapshot])
    mutate = Mock(return_value=({("quotas", "q"): {"count": 1}}, "created"))
    assert await store.atomic([("quotas", "q")], mutate) == "created"
    mutate.assert_called_once_with({("quotas", "q"): None})
    assert reference.get.call_count == 2
    assert sum(transaction._commit.call_count for transaction in transactions) == 1
    transactions[-1].set.assert_called_once()


async def test_read_retries_are_bounded_and_exhaustion_is_a_busy_response():
    store, reference, transactions = firestore_store([Aborted("contention")] * 3)
    mutate = Mock()
    with pytest.raises(AppError) as error:
        await store.atomic([("quotas", "q")], mutate)
    assert error.value.status == 409 and error.value.code == "transaction_busy"
    assert reference.get.call_count == 3 and len(transactions) == 3
    mutate.assert_not_called()


async def test_exhausted_sdk_commit_budget_is_not_multiplied():
    snapshot = Mock(exists=False)
    store, reference, transactions = firestore_store([snapshot] * 5, commit_error=Aborted("commit"))
    with pytest.raises(AppError) as error:
        await store.atomic([("quotas", "q")], lambda docs: ({}, None))
    assert error.value.code == "transaction_busy"
    assert len(transactions) == 1 and transactions[0]._commit.call_count == 5


async def test_business_validation_errors_are_not_retried_or_disguised():
    snapshot = Mock(exists=False)
    store, reference, transactions = firestore_store([snapshot])
    mutate = Mock(side_effect=ValueError("invalid business state"))
    with pytest.raises(ValueError, match="invalid business state"):
        await store.atomic([("quotas", "q")], mutate)
    assert reference.get.call_count == 1 and len(transactions) == 1
