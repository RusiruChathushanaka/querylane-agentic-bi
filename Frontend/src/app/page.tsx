import type { Metadata } from "next";
import Link from "next/link";
import {
  ArrowDown,
  ArrowRight,
  ArrowUpRight,
  AudioLines,
  BookOpen,
  ChartNoAxesCombined,
  Check,
  Database,
  FileChartColumn,
  GitBranch,
  Globe2,
  LayoutDashboard,
  MessageSquareText,
  SearchCheck,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { HeroProduct } from "@/components/landing/product-illustrations";
import { ProductTour } from "@/components/landing/product-tour";
import { LandingMobileNavigation } from "@/components/landing/mobile-navigation";
import { workspacePath } from "@/lib/workspace-links";

const origin = "https://agentic-bi-frontend-wekihucn7q-as.a.run.app";
const description =
  "Ask by voice or text. Build evidence-backed reports, compare TimesFM 3.0 Preview forecasts and explore explicit what-if scenarios in Querylane's public synthetic retail demo. No sign-up.";
export const metadata: Metadata = {
  title: "Querylane — From questions to evidence-backed decisions",
  description,
  alternates: { canonical: origin },
  openGraph: {
    type: "website",
    url: origin,
    siteName: "Querylane",
    title: "Your next business decision starts with a question.",
    description,
    images: [
      {
        url: `${origin}/querylane-social.png`,
        width: 1200,
        height: 630,
        alt: "Querylane: conversational BI, advanced reports and validated predictions",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Querylane — Evidence-backed business intelligence",
    description,
    images: [`${origin}/querylane-social.png`],
  },
};

function OpenQuerylane({ light = false }: { light?: boolean }) {
  return (
    <Link
      prefetch={false}
      href={workspacePath()}
      className={`landing-cta ${light ? "landing-cta-light" : ""}`}
    >
      Open Querylane <ArrowUpRight size={18} aria-hidden />
    </Link>
  );
}

const capabilities = [
  {
    icon: MessageSquareText,
    number: "01",
    title: "Ask. Follow up. Explore.",
    text: "Natural-language questions with context that carries forward. Browse public history, fork a conversation and choose your model.",
    example: "“Now break that down by region.”",
  },
  {
    icon: Database,
    number: "02",
    title: "Bring sources together.",
    text: "Schema-aware SQL for BigQuery and PostgreSQL. Explore across sources with inferred relationships and visible join assumptions.",
    example: "Sales + customer profiles + regional targets",
  },
  {
    icon: ChartNoAxesCombined,
    number: "03",
    title: "Find the story in the chart.",
    text: "Seven visualization types with highlights, exact-value tooltips, series and range controls, comparisons and chart-to-chat follow-ups.",
    example: "Inspect a point. Ask the next question.",
  },
  {
    icon: LayoutDashboard,
    number: "04",
    title: "Build a shared view.",
    text: "Pin charts, tables and KPIs. Arrange cards in Edit mode, explore in View mode, share a public link and download the dashboard.",
    example: "Saved results. Recoverable deletion. No refresh queries.",
  },
  {
    icon: BookOpen,
    number: "05",
    title: "Teach it your business.",
    text: "Create shared, versioned skills. Attach them or let the agent select relevant guidance. Import Markdown, export it, or draft a skill conversationally and review before publishing.",
    example: "Definitions and playbooks, with version evidence",
  },
  {
    icon: SearchCheck,
    number: "06",
    title: "Take the evidence with you.",
    text: "Inspect SQL, units, completeness, source timestamps and skill versions. Export charts, saved-result CSVs, dashboards and report documents in their supported formats.",
    example: "From an interesting answer to inspectable evidence",
  },
];
const faqs = [
  [
    "Do I need an account? Is my work private?",
    "No account is required. This is a public demo using synthetic retail data. Conversations, skills, reports and dashboards are shared, and other visitors can manage shared library items. Do not enter private information or credentials.",
  ],
  [
    "Which databases does Querylane support?",
    "The application connects to administrator-configured BigQuery and PostgreSQL sources. The demo uses a larger generated retail dataset. Visitors do not enter database credentials. Private on-premises connectivity and other database engines are future extensions.",
  ],
  [
    "How long does an advanced report take?",
    "Allow several minutes, typically around 3–8 minutes depending on scope and service availability. The report shows meaningful progress, supports cancellation by its requester, and can be reopened after navigating away. Ordinary chat remains available while it runs.",
  ],
  [
    "How does Querylane choose TimesFM?",
    "The agent proposes relevant forecasting work. TimesFM 3.0 Preview is compared with eligible statistical methods on the same chronological backtest periods. Numerical validation selects the published method; TimesFM is not guaranteed to win. Saved model scores, cutoffs and assumptions remain inspectable in the report.",
  ],
  [
    "What does a scenario tell me?",
    "A scenario predicts under explicit future assumptions you provide, such as alternative promotion schedules. Baseline and alternative use the same validated model and history. Conditional backtests assume those driver paths are known; they do not prove the drivers are predictable or that a promotion causes revenue lift.",
  ],
  [
    "Can I rely on every prediction?",
    "Predictions are conditional estimates, not guarantees. Forecasts are checked with chronological backtests and baseline comparisons. Short histories, incomplete data or poor validation can withhold a forecast. Scenarios require explicit future driver assumptions; observational relationships do not prove causation.",
  ],
  [
    "Do dashboards automatically query fresh data?",
    "No. Dashboard cards reference saved results and their published views. Pinning a result or opening a dashboard runs no new source queries. Request another analysis when you need updated data, and pin that saved result explicitly.",
  ],
  [
    "What can I download?",
    "Reports support PDF, editable Word documents and saved-result CSV data bundles. Individual charts support PNG and CSV; dashboards offer image, PDF and saved-data formats. Downloads retain their relevant scope and completeness notes. Available formats depend on the artifact.",
  ],
];

export default function LandingPage() {
  return (
    <div className="landing-page">
      <a className="landing-skip" href="#landing-content">
        Skip to content
      </a>
      <header className="landing-header landing-container">
        <Link href="/" className="landing-brand" aria-label="Querylane home">
          <span className="landing-brand-mark" aria-hidden>
            <GitBranch size={22} />
          </span>
          Querylane<span className="landing-brand-period">.</span>
        </Link>
        <nav className="landing-desktop-nav" aria-label="Landing navigation">
          <a href="#reports">Reports</a>
          <a href="#predictions">Predictions</a>
          <a href="#voice-bi">Voice BI</a>
          <a href="#capabilities">Capabilities</a>
        </nav>
        <div className="landing-header-actions">
          <OpenQuerylane />
          <LandingMobileNavigation />
        </div>
      </header>
      <main id="landing-content" tabIndex={-1}>
        <section
          className="landing-hero landing-container"
          aria-labelledby="hero-title"
        >
          <div className="landing-hero-copy">
            <p className="landing-eyebrow">
              <span /> INTELLIGENCE THAT MOVES BUSINESS FORWARD
            </p>
            <h1 id="hero-title">
              From business questions to <em>evidence-backed</em> decisions.
            </h1>
            <p className="landing-hero-description">
              Meet your conversational AI analyst. Ask by voice or text, build
              detailed reports, explore TimesFM forecasts and explicit what-if
              scenarios, and bring the findings together in shared dashboards.
            </p>
            <div className="landing-hero-actions">
              <OpenQuerylane />
              <a href="#guided-preview" className="landing-text-link">
                Explore the product <ArrowDown size={16} aria-hidden />
              </a>
            </div>
            <p className="landing-hero-assurance">
              <span>
                <Check size={15} aria-hidden />
                No sign-up
              </span>
              <span>
                <Globe2 size={15} aria-hidden />
                Public retail demo
              </span>
            </p>
          </div>
          <HeroProduct />
        </section>
        <section
          className="landing-scale landing-container"
          aria-label="Synthetic retail dataset scale"
        >
          <p>
            A real analytical playground.
            <br />
            <strong>Entirely synthetic retail data.</strong>
          </p>
          <dl>
            <div>
              <dt>Orders</dt>
              <dd>573,348</dd>
            </div>
            <div>
              <dt>Line items</dt>
              <dd>1.3 million</dd>
            </div>
            <div>
              <dt>History</dt>
              <dd>45 months</dd>
            </div>
          </dl>
          <span>
            Jan 2023
            <br />
            Sep 2026
          </span>
        </section>
        <section
          className="landing-section landing-container"
          aria-labelledby="advanced-title"
        >
          <div className="landing-section-heading">
            <p className="landing-eyebrow">MORE THAN AN ANSWER</p>
            <h2 id="advanced-title">
              The depth of an analyst.
              <br />
              The simplicity of a conversation.
            </h2>
            <p>
              Move from a quick question to a considered decision—with the work
              behind it always in view.
            </p>
          </div>
          <div className="landing-advanced-intro">
            <article id="reports">
              <FileChartColumn aria-hidden />
              <h3>Reports with substance</h3>
              <p>
                Coordinated analysis, findings and methodology in one
                downloadable report.
              </p>
            </article>
            <article id="predictions">
              <TrendingUp aria-hidden />
              <h3>TimesFM forecasts &amp; scenarios</h3>
              <p>
                Compare Google TimesFM 3.0 Preview with statistical methods.
                Explore alternative futures with visible assumptions.
              </p>
            </article>
            <article id="voice-bi">
              <AudioLines aria-hidden />
              <h3>BI that talks back</h3>
              <p>
                A live analyst conversation, with transcripts and charts that
                help you keep exploring.
              </p>
            </article>
          </div>
          <div id="guided-preview" className="landing-preview-anchor">
            <ProductTour />
          </div>
        </section>
        <section className="landing-workflow" aria-labelledby="workflow-title">
          <div className="landing-container">
            <div className="landing-section-heading">
              <p className="landing-eyebrow">A CLEAR PATH THROUGH THE DATA</p>
              <h2 id="workflow-title">One question. Many ways forward.</h2>
              <p>Start small. Go deeper when the decision calls for it.</p>
            </div>
            <ol className="landing-workflow-steps">
              <li>
                <span>01</span>
                <MessageSquareText aria-hidden />
                <h3>Ask a business question</h3>
                <p>Type or talk. Keep context with natural follow-ups.</p>
              </li>
              <li>
                <span>02</span>
                <ChartNoAxesCombined aria-hidden />
                <h3>Explore the answer</h3>
                <p>Inspect charts, exact values, SQL and source evidence.</p>
              </li>
              <li>
                <span>03</span>
                <FileChartColumn aria-hidden />
                <h3>Request deeper analysis</h3>
                <p>
                  Build a detailed report. Compare forecasting methods and
                  explicit scenarios when the evidence supports them.
                </p>
              </li>
              <li>
                <span>04</span>
                <LayoutDashboard aria-hidden />
                <h3>Keep what matters</h3>
                <p>
                  Pin useful results, share a dashboard and download the
                  evidence.
                </p>
              </li>
            </ol>
          </div>
        </section>
        <section
          id="capabilities"
          className="landing-section landing-container"
          aria-labelledby="capabilities-title"
        >
          <div className="landing-heading-row">
            <div>
              <p className="landing-eyebrow">A CONNECTED BI WORKSPACE</p>
              <h2 id="capabilities-title">
                Every insight has
                <br />
                somewhere to go.
              </h2>
            </div>
            <p>
              From your first question to your next business review, the tools
              stay connected.
            </p>
          </div>
          <div className="landing-capabilities">
            {capabilities.map(
              ({ icon: Icon, number, title, text, example }) => (
                <article key={number}>
                  <div className="landing-capability-top">
                    <Icon aria-hidden />
                    <span>{number}</span>
                  </div>
                  <h3>{title}</h3>
                  <p>{text}</p>
                  <small>{example}</small>
                </article>
              ),
            )}
          </div>
        </section>
        <section
          className="landing-evidence landing-container"
          aria-labelledby="evidence-title"
        >
          <div>
            <p className="landing-eyebrow">CONFIDENCE COMES FROM VISIBILITY</p>
            <h2 id="evidence-title">
              Don’t just read the answer.
              <br />
              Inspect the work.
            </h2>
            <p>
              Querylane keeps evidence close: saved results, source SQL,
              independent timestamps, completeness, definitions and stated
              assumptions.
            </p>
            <ul className="landing-checks">
              <li>
                <ShieldCheck aria-hidden />
                Controlled, read-only analytical access
              </li>
              <li>
                <GitBranch aria-hidden />
                Coordinated Google ADK workflows
              </li>
              <li>
                <BookOpen aria-hidden />
                Captured skill versions behind each analysis
              </li>
            </ul>
          </div>
          <div className="landing-evidence-card">
            <div>
              <span className="landing-evidence-status">
                <Check size={14} aria-hidden />
                SAVED EVIDENCE
              </span>
              <span>Synthetic demo</span>
            </div>
            <h3>What does “revenue” mean?</h3>
            <p>
              Merchandise revenue after item discounts, before refunds, tax and
              shipping.
            </p>
            <dl>
              <div>
                <dt>Scope</dt>
                <dd>Completed orders · Jan 2023–Sep 2026</dd>
              </div>
              <div>
                <dt>Provenance</dt>
                <dd>Source SQL, run timestamps &amp; saved artifacts</dd>
              </div>
              <div>
                <dt>Boundaries</dt>
                <dd>Assumptions and incomplete results stay visible</dd>
              </div>
            </dl>
            <span className="landing-evidence-bottom">
              <Database size={15} aria-hidden />
              BigQuery + PostgreSQL <ArrowRight size={15} aria-hidden />{" "}
              Controlled analysis
            </span>
          </div>
        </section>
        <div className="landing-technology landing-container">
          <span>Built with</span>
          <strong>Google ADK</strong>
          <span>+</span>
          <strong>Gemini</strong>
          <span>+</span>
          <strong>TimesFM 3.0 · Preview</strong>
          <i />
          <span>BigQuery</span>
          <span>PostgreSQL</span>
          <span>Firestore</span>
          <span>Cloud Run</span>
        </div>
        <section
          className="landing-faq landing-section landing-container"
          aria-labelledby="faq-title"
        >
          <div>
            <p className="landing-eyebrow">BEFORE YOU EXPLORE</p>
            <h2 id="faq-title">
              Good questions.
              <br />
              Clear answers.
            </h2>
            <p>Know what you’re opening—and what to expect.</p>
          </div>
          <div className="landing-faq-items">
            {faqs.map(([question, answer]) => (
              <details key={question}>
                <summary>
                  {question}
                  <span aria-hidden>+</span>
                </summary>
                <p>{answer}</p>
              </details>
            ))}
          </div>
        </section>
        <section
          className="landing-closing landing-container"
          aria-labelledby="closing-title"
        >
          <span className="landing-closing-icon">
            <Sparkles size={26} aria-hidden />
          </span>
          <p className="landing-eyebrow">YOUR NEXT QUESTION IS A GOOD START</p>
          <h2 id="closing-title">
            Make room for
            <br />
            your next insight.
          </h2>
          <p>
            Explore reports, TimesFM forecasts, scenarios and voice BI.
            <br />
            No sign-up. A shared workspace. Synthetic retail data.
          </p>
          <OpenQuerylane light />
        </section>
      </main>
      <footer className="landing-footer landing-container">
        <div>
          <Link href="/" className="landing-brand">
            Querylane<span className="landing-brand-period">.</span>
          </Link>
          <p>Business intelligence, in conversation.</p>
        </div>
        <nav aria-label="Public libraries">
          <Link prefetch={false} href="/reports">
            Reports
          </Link>
          <Link prefetch={false} href="/dashboards">
            Dashboards
          </Link>
          <Link prefetch={false} href="/skills">
            Skills
          </Link>
          <OpenQuerylane />
        </nav>
        <p className="landing-footer-note">
          Public competition demo · All shared content is visible to other
          visitors.
        </p>
      </footer>
    </div>
  );
}
