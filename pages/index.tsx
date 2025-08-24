
import type { NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import styles from "../styles/Home.module.css";

const Home: NextPage = () => {
  return (
    <div className={styles.container}>
      <Head>
        <title>IntelliShop - Payment Provider for Agent Shopping</title>
        <meta name="description" content="Payment provider enabling AI agents to safely manage shopping transactions with intelligent payment orchestration." />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <nav className={styles.nav}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>💳</span>
          IntelliShop
        </div>
        <div className={styles.navLinks}>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
          <a href="#docs">Documentation</a>
          <Link href="/business-orchestration">
            <button className={styles.loginButton} style={{ marginRight: '10px' }}>Business Portal</button>
          </Link>
          <Link href="/dashboard">
            <button className={styles.loginButton}>Dashboard</button>
          </Link>
        </div>
      </nav>

      <main className={styles.main}>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.badge}>PAYMENT PROVIDER • AI AGENT COMMERCE</div>
            <h1 className={styles.heroTitle}>
              Intelligent Payment Infrastructure for AI Agents
            </h1>
            <p className={styles.heroDescription}>
              Payment provider enabling Future Shopping Agents from OpenAI, Visa, and Perplexity to safely initiate, reroute, and complete purchases with trusted payment orchestration.
            </p>

            <div className={styles.savingsSection}>
              <div className={styles.savingsAmount}>$2.4M</div>
              <div className={styles.savingsLabel}>Revenue Protected <span className={styles.tooltip}>?</span></div>
              
              <div className={styles.slider}>
                <div className={styles.sliderTrack}>
                  <div className={styles.sliderFill}></div>
                  <div className={styles.sliderHandle}></div>
                </div>
                <div className={styles.sliderLabels}>
                  <span>$500K</span>
                  <span className={styles.sliderCenter}>$1.2M<br/>Transaction Volume</span>
                  <span>$5M+</span>
                </div>
              </div>
            </div>

            <div className={styles.demoCard}>
              <div className={styles.demoHeader}>
                <span className={styles.demoLabel}>AGENT FEATURE</span>
                <div className={styles.approvedBadge}>
                  <span className={styles.approvedNumber}>24</span>
                  <span className={styles.approvedText}>AGENTS<br/>APPROVED</span>
                </div>
              </div>
              <h2 className={styles.demoTitle}>Payment Provider for Agent Shopping</h2>
              <p className={styles.demoDescription}>
                Use MCP to call, route, and orchestrate payments with intelligent processor selection and compliance boundaries for autonomous shopping experiences.
              </p>
              <div className={styles.demoFeatures}>
                <div className={styles.demoFeature}>
                  <span className={styles.featureIcon}>💳</span>
                  Secure Payment Processing
                </div>
                <div className={styles.demoFeature}>
                  <span className={styles.featureIcon}>🤖</span>
                  AI Agent Integration
                </div>
                <div className={styles.demoFeature}>
                  <span className={styles.featureIcon}>🔄</span>
                  Smart Routing & Fallbacks
                </div>
              </div>
            </div>

            <div className={styles.heroButtons}>
              <Link href="/business-orchestration">
                <button className={styles.primaryButton}>Launch Business Portal</button>
              </Link>
              <Link href="/dashboard">
                <button className={styles.secondaryButton}>View Analytics</button>
              </Link>
            </div>
          </div>
        </section>

        <section id="features" className={styles.features}>
          <h2 className={styles.sectionTitle}>Trusted by AI Agents Worldwide</h2>
          <div className={styles.featureGrid}>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🤖</div>
              <h3>MCP Integration</h3>
              <p>Native Model Context Protocol support for seamless agent communication and shopping context management.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🔄</div>
              <h3>Smart Rerouting</h3>
              <p>Intelligent payment processor fallbacks when primary routes fail, maintaining transaction continuity.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>🛡️</div>
              <h3>Compliance First</h3>
              <p>Built-in compliance boundaries and human-in-the-loop controls for secure autonomous shopping.</p>
            </div>
            <div className={styles.featureCard}>
              <div className={styles.featureIcon}>📊</div>
              <h3>Full Transparency</h3>
              <p>Complete audit trails and decision reasoning for trust and regulatory compliance.</p>
            </div>
          </div>
        </section>

        <section className={styles.cta}>
          <h2>Ready to enable autonomous shopping?</h2>
          <p>Join the future of AI-powered commerce with IntelliShop&apos;s payment provider.</p>
          <Link href="/dashboard">
            <button className={styles.ctaButtonLarge}>Get Started Today</button>
          </Link>
        </section>
      </main>

      <footer className={styles.footer}>
        <p>© 2024 IntelliShop. Powering the future of agentic commerce.</p>
      </footer>
    </div>
  );
};

export default Home;
