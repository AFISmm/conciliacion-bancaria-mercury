import "server-only";
import crypto from "node:crypto";

const ITERATIONS = 200_000;
const KEYLEN = 32;
const DIGEST = "sha256";

function pbkdf2(password: string, salt: Buffer): Promise<Buffer> {
  return new Promise((resolve, reject) => {
    crypto.pbkdf2(password, salt, ITERATIONS, KEYLEN, DIGEST, (err, derivedKey) => {
      if (err) reject(err);
      else resolve(derivedKey);
    });
  });
}

// Same "saltHex:keyHex" pbkdf2-sha256 scheme as the original Python app
// (hashlib.pbkdf2_hmac), so existing password hashes don't need re-hashing.
export async function hashPassword(password: string): Promise<string> {
  const salt = crypto.randomBytes(16);
  const key = await pbkdf2(password, salt);
  return `${salt.toString("hex")}:${key.toString("hex")}`;
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const [saltHex, keyHex] = stored.split(":");
  if (!saltHex || !keyHex) return false;
  const salt = Buffer.from(saltHex, "hex");
  const expected = Buffer.from(keyHex, "hex");
  const key = await pbkdf2(password, salt);
  return key.length === expected.length && crypto.timingSafeEqual(key, expected);
}

export function generateVerificationCode(): string {
  return crypto.randomInt(100_000, 1_000_000).toString();
}
