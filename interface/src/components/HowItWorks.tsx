export default function HowItWorks() {
  const steps = [
    'Enter a URL',
    'Unitron analyzes core, adjacent, broader vendors',
    'View results inline',
  ]
  return (
    <section data-observe>
      <div className="max-w-6xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-8">How It Works</h2>
        <div className="flex flex-col md:flex-row md:justify-center md:space-x-12 space-y-6 md:space-y-0">
          {steps.map((s, i) => (
            <div key={i} className="flex items-start md:flex-col md:items-center text-center">
              <span className="w-8 h-8 flex items-center justify-center rounded-full bg-primary text-white font-semibold">
                {i + 1}
              </span>
              <span className="ml-3 md:ml-0 md:mt-3 text-sm font-medium">{s}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
