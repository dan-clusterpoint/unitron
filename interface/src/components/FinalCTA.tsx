export default function FinalCTA() {
  return (
    <section className="cta-section text-white" data-observe>
      <div className="max-w-6xl mx-auto px-6 text-center">
        <h2 className="text-3xl font-bold mb-4">Start Analyzing Today</h2>
        <button
          onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
          className="btn-primary"
        >
          Get Started
        </button>
      </div>
    </section>
  )
}
