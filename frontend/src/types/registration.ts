export interface RegistrationFormData {
  studentName: string;
  studentEmail: string;
  experienceLevel: "beginner" | "intermediate" | "advanced";
  specialRequests?: string;
}

export interface RegistrationSubmission {
  id: string;
  workflowId: string;
  studentName: string;
  studentEmail: string;
  feeAmount: number;
  currency: string;
  paymentStatus: "unpaid" | "verifying" | "paid" | "failed";
  paypalTransactionId?: string;
  emailConfirmed: boolean;
  registeredAt: string;
}
