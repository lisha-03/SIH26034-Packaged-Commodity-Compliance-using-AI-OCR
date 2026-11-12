export default function StatusBadge({ status }) {
  const key = (status || '').toLowerCase()
  const labelMap = {
    pass: 'PASS',
    fail: 'FAIL',
    warning: 'WARNING',
    manual_verification: 'MANUAL VERIFICATION',
    not_applicable: 'NOT APPLICABLE',
    compliant: 'COMPLIANT',
    non_compliant: 'NON-COMPLIANT',
    needs_review: 'NEEDS REVIEW',
  }
  const emojiMap = {
    compliant: '🟢',
    needs_review: '🟡',
    non_compliant: '🔴',
  }
  return (
    <span className={`badge badge-${key}`}>
      {emojiMap[key] ? emojiMap[key] + ' ' : ''}
      {labelMap[key] || status}
    </span>
  )
}
