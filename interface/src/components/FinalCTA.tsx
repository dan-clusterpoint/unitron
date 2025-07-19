export default function FinalCTA() {
  return (
    <section className="bg-dark text-white" data-observe>
      <div className="max-w-6xl mx-auto px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-4">Start Analyzing Today</h2>
        <button
          onClick={() => document.getElementById('analyzer')?.scrollIntoView({ behavior: 'smooth' })}
          className="bg-primary hover:bg-primary-dark px-6 py-3 rounded transition"
        >
          Get Started
        </button>
      </div>
    </section>
  )
}
