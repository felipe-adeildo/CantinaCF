export type PaymentMethodStats = {
  paymentMethod: string
  value: number
}[]

export type ProductSaleStats = {
  product: string
  value: number
}[]

export type TStats = {
  paymentMethodQuantity: PaymentMethodStats
  paymentMethodMoney: PaymentMethodStats
  productQuantity: ProductSaleStats
}
