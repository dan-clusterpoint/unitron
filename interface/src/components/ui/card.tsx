import { forwardRef, HTMLAttributes } from 'react'
import clsx from 'clsx'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {}

export const Card = forwardRef<HTMLDivElement, CardProps>(function Card({ className, ...props }, ref) {
  return <div ref={ref} className={clsx('rounded-lg border bg-white shadow-sm', className)} {...props} />
})

export const CardHeader = forwardRef<HTMLDivElement, CardProps>(function CardHeader({ className, ...props }, ref) {
  return <div ref={ref} className={clsx('p-4 border-b', className)} {...props} />
})

export const CardContent = forwardRef<HTMLDivElement, CardProps>(function CardContent({ className, ...props }, ref) {
  return <div ref={ref} className={clsx('p-4', className)} {...props} />
})

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(function CardTitle({ className, ...props }, ref) {
  return <h3 ref={ref} className={clsx('text-lg font-semibold', className)} {...props} />
})
