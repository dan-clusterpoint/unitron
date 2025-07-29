import { forwardRef } from 'react'
import * as Primitive from '@radix-ui/react-accordion'
import clsx from 'clsx'

export const Accordion = Primitive.Root

export const AccordionItem = forwardRef<
  React.ElementRef<typeof Primitive.Item>,
  React.ComponentPropsWithoutRef<typeof Primitive.Item>
>(function AccordionItem({ className, ...props }, ref) {
  return <Primitive.Item ref={ref} className={clsx('border-b', className)} {...props} />
})

export const AccordionTrigger = forwardRef<
  React.ElementRef<typeof Primitive.Trigger>,
  React.ComponentPropsWithoutRef<typeof Primitive.Trigger>
>(function AccordionTrigger({ className, children, ...props }, ref) {
  return (
    <Primitive.Header className="flex">
      <Primitive.Trigger
        ref={ref}
        className={clsx(
          'flex flex-1 items-center justify-between py-4 font-medium hover:underline',
          className,
        )}
        {...props}
      >
        {children}
        <svg
          className="h-4 w-4 shrink-0 transition-transform duration-200"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </Primitive.Trigger>
    </Primitive.Header>
  )
})

export const AccordionContent = forwardRef<
  React.ElementRef<typeof Primitive.Content>,
  React.ComponentPropsWithoutRef<typeof Primitive.Content>
>(function AccordionContent({ className, children, ...props }, ref) {
  return (
    <Primitive.Content
      ref={ref}
      className={clsx('overflow-hidden data-[state=open]:animate-accordion-down', className)}
      {...props}
    >
      <div className="pb-4 pt-0 text-sm">{children}</div>
    </Primitive.Content>
  )
})
