import "server-only";
import { Resend } from "resend";

export async function sendVerificationCode(
  to: string,
  code: string,
): Promise<{ sent: boolean; message: string }> {
  const apiKey = process.env.RESEND_API_KEY;
  const from = process.env.EMAIL_FROM;
  if (!apiKey || !from) return { sent: false, message: "RESEND_NOT_CONFIGURED" };

  const html = `
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;">
      <div style="background:#2c3e50;color:#fff;padding:22px 28px;border-radius:8px 8px 0 0;">
        <h2 style="margin:0;font-size:1.2rem;">🏦 Conciliación Bancaria</h2>
        <p style="margin:4px 0 0;opacity:.75;font-size:.8rem;">Mercury Methods Ltda</p>
      </div>
      <div style="padding:32px 28px;border:1px solid #e0e0e0;border-top:none;border-radius:0 0 8px 8px;">
        <p style="color:#424242;margin-top:0;">Su código de verificación es:</p>
        <div style="text-align:center;margin:28px 0;">
          <span style="font-size:42px;font-weight:700;letter-spacing:14px;
                       color:#2c3e50;background:#f5f5f5;padding:14px 28px;border-radius:8px;">
            ${code}
          </span>
        </div>
        <p style="color:#757575;font-size:.78rem;">
          Este código expira en <strong>10 minutos</strong>.<br>
          Si no solicitó este código, ignore este mensaje.
        </p>
      </div>
    </div>
  `;

  try {
    const resend = new Resend(apiKey);
    const { error } = await resend.emails.send({
      from: `Conciliación Bancaria Mercury <${from}>`,
      to,
      subject: "Código de verificación – Conciliación Bancaria Mercury",
      html,
    });
    if (error) return { sent: false, message: error.message };
    return { sent: true, message: "" };
  } catch (err) {
    return { sent: false, message: err instanceof Error ? err.message : String(err) };
  }
}
