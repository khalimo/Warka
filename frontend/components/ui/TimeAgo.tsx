'use client'

import { formatDistanceToNow } from 'date-fns'

export function TimeAgo({ date }: { date: string }) {
  return <time dateTime={date}>{formatDistanceToNow(new Date(date), { addSuffix: true })}</time>
}
