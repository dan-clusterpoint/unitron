import { HeartIcon, ChartBarIcon, HomeIcon, RocketLaunchIcon } from '@heroicons/react/24/outline'

export default function FeatureGrid() {
  const features = [
    {
      title: 'Healthchecks',
      desc: 'Automated readiness and liveness probes',
      icon: <HeartIcon className="w-8 h-8 md:w-6 md:h-6 lg:scale-90 text-primary" />,
    },
    {
      title: 'Property Analysis',
      desc: 'Reverse-engineer key site details',
      icon: <HomeIcon className="w-8 h-8 md:w-6 md:h-6 lg:scale-90 text-primary" />,
    },
    {
      title: 'Martech Analysis',
      desc: 'Detect marketing technologies in use',
      icon: <ChartBarIcon className="w-8 h-8 md:w-6 md:h-6 lg:scale-90 text-primary" />,
    },
    {
      title: 'Pipeline Runner',
      desc: 'Automate data flows end-to-end',
      icon: <RocketLaunchIcon className="w-8 h-8 md:w-6 md:h-6 lg:scale-90 text-primary" />,
    },
  ]
  return (
    <section className="bg-gray-50" data-observe>
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((f) => (
            <div key={f.title} className="bg-white p-6 rounded-lg shadow text-center space-y-2">
              <div className="flex justify-center">{f.icon}</div>
              <h3 className="font-semibold text-lg">{f.title}</h3>
              <p className="text-sm text-neutral leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
