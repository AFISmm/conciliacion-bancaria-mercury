export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-100 p-4">
      <div className="w-full max-w-sm overflow-hidden rounded-xl bg-white shadow-lg">
        <div className="bg-[#2c3e50] px-7 py-7 text-center text-white">
          <div className="text-3xl">🏦</div>
          <h2 className="mt-2 text-lg font-bold">Conciliación Bancaria</h2>
          <p className="mt-1 text-xs opacity-75">Mercury Methods Ltda</p>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}
