"use client"

import { RechargesFilters } from "@/components/audits/recharges/filters"
import { RechargesTable } from "@/components/audits/recharges/table"
import { LoginRequired } from "@/components/login-required"
import { TBRechargesQuery } from "@/types/queries"
import { useState } from "react"

const Recharges = () => {
  const query = useState<TBRechargesQuery>({})
  return (
    <>
      <h1 className="text-xl my-2 text-center">Histórico de Recargas</h1>
      <RechargesFilters query={query} />
      <RechargesTable query={query} />
    </>
  )
}

const ProtectedRecharges = () => {
  return (
    <LoginRequired allowed_roles={[1]}>
      <Recharges />
    </LoginRequired>
  )
}

export default ProtectedRecharges
