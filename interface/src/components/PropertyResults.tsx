export default function PropertyResults({
  property,
}: {
  property: { confidence: number }
}) {
  return (
    <div className="bg-gray-50 p-4 rounded mb-4">
      <h3 className="font-medium">Confidence</h3>
      <p>{Math.round(property.confidence * 100)}%</p>
    </div>
  )
}
