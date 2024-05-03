"use client"

import { LoginRequired } from "@/components/login-required"
import { PaymentRequest } from "@/components/payments/payment-request"
import { usePayments } from "@/hooks/payments"
import { Loader2 } from "lucide-react"

const Payments = () => {
  const { payments, isLoading } = usePayments()
  return (
    <div>
      <h1 className="text-xl my-4 text-center">Verificação de Pagmentos</h1>

      {isLoading && (
        <div className="flex justify-center items-center mt-32">
          <Loader2 className="animate-spin" />
          <span className="text-xl ml-2">Carregando...</span>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
        {payments.map((payment) => (
          <PaymentRequest key={payment.id} payment={payment} />
        ))}
      </div>
    </div>
  )
}

const ProtectedPayments = () => {
  return (
    <LoginRequired allowed_roles={[1]}>
      <Payments />
    </LoginRequired>
  )
}

export default ProtectedPayments