export const validateInn = (inn: string): boolean => {
  const cleaned = inn.replace(/\s/g, '')
  if (!/^\d{10}$|^\d{12}$/.test(cleaned)) return false

  if (cleaned.length === 10) {
    const weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
    const sum = weights.reduce((acc, w, i) => acc + w * parseInt(cleaned[i]), 0)
    const checksum = (sum % 11) % 10
    return checksum === parseInt(cleaned[9])
  }

  if (cleaned.length === 12) {
    const weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    const weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    const sum1 = weights1.reduce((acc, w, i) => acc + w * parseInt(cleaned[i]), 0)
    const sum2 = weights2.reduce((acc, w, i) => acc + w * parseInt(cleaned[i]), 0)
    const checksum1 = (sum1 % 11) % 10
    const checksum2 = (sum2 % 11) % 10
    return checksum1 === parseInt(cleaned[10]) && checksum2 === parseInt(cleaned[11])
  }

  return false
}

export const validateEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

export const validatePhone = (phone: string): boolean => {
  const cleaned = phone.replace(/[\s\-\(\)]/g, '')
  return /^\+?\d{10,15}$/.test(cleaned)
}

export const validateAmount = (amount: string): boolean => {
  const num = parseFloat(amount.replace(/\s/g, '').replace(',', '.'))
  return !isNaN(num) && num > 0
}

export const validateRequired = (value: string | null | undefined): boolean => {
  return value != null && value.trim().length > 0
}
