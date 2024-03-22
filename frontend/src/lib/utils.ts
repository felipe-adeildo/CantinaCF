import { AxiosError, AxiosResponse } from "axios"
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getResponseErrorMessage(response: AxiosResponse): string {
  const data = response.data as { message?: string }
  if (data && data.message) {
    return data.message
  } else {
    return "Um erro inesperado aconteceu."
  }
}

export function getErrorMessage(error: AxiosError): string {
  if (error.response) {
    return getResponseErrorMessage(error.response)
  } else if (error.request) {
    return "Sem resposta da API."
  } else {
    return error.message
  }
}
