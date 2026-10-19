-- WORTH? Premium — setup aman untuk QRIS + verifikasi manual.
-- Jalankan SELURUH file ini di Supabase Dashboard > SQL Editor sebagai pemilik proyek.
-- Skrip ini mempertahankan 20 kode yang sudah ada; tidak membuat kode baru.
-- Tinjau skrip sebelum menjalankan. Admin tetap harus memverifikasi uang masuk secara nyata.

BEGIN;

-- A. Tutup akses langsung pengguna ke tabel kode. Aktivasi hanya lewat RPC.
REVOKE ALL ON TABLE public.activation_codes FROM PUBLIC, anon, authenticated;

-- B. Pesanan: pengguna login hanya boleh membaca pesanan sendiri dan membuat pesanan PENDING Rp9.900.
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
DO $policies$
DECLARE p record;
BEGIN
  FOR p IN SELECT policyname FROM pg_catalog.pg_policies
           WHERE schemaname = 'public' AND tablename = 'orders'
  LOOP
    EXECUTE pg_catalog.format('DROP POLICY IF EXISTS %I ON public.orders', p.policyname);
  END LOOP;
END;
$policies$;
REVOKE ALL ON TABLE public.orders FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.orders TO authenticated;
GRANT INSERT (user_id, amount, payment_status, customer_email)
  ON TABLE public.orders TO authenticated;
CREATE POLICY orders_select_own
  ON public.orders FOR SELECT TO authenticated
  USING (user_id = (SELECT auth.uid()));
CREATE POLICY orders_insert_own_pending
  ON public.orders FOR INSERT TO authenticated
  WITH CHECK (
    user_id = (SELECT auth.uid())
    AND amount = 9900
    AND payment_status = 'PENDING'
    AND verified_at IS NULL
  );

-- C. Profil: pengguna hanya dapat mengubah kolom profil/pemakaian, bukan kolom Premium.
-- Hak UPDATE kolom Premium tidak diberikan kepada authenticated; RPC SECURITY DEFINER yang mengubahnya.
ALTER TABLE public.worth_users ENABLE ROW LEVEL SECURITY;
DO $policies$
DECLARE p record;
BEGIN
  FOR p IN SELECT policyname FROM pg_catalog.pg_policies
           WHERE schemaname = 'public' AND tablename = 'worth_users'
  LOOP
    EXECUTE pg_catalog.format('DROP POLICY IF EXISTS %I ON public.worth_users', p.policyname);
  END LOOP;
END;
$policies$;
ALTER TABLE public.worth_users ALTER COLUMN is_premium SET DEFAULT false;
REVOKE ALL ON TABLE public.worth_users FROM PUBLIC, anon, authenticated;
GRANT SELECT ON TABLE public.worth_users TO authenticated;
GRANT INSERT (user_id, email, name, usage_date, daily_checks, history, updated_at)
  ON TABLE public.worth_users TO authenticated;
GRANT UPDATE (email, name, usage_date, daily_checks, history, updated_at)
  ON TABLE public.worth_users TO authenticated;
CREATE POLICY worth_users_select_own
  ON public.worth_users FOR SELECT TO authenticated
  USING (user_id = (SELECT auth.uid()));
CREATE POLICY worth_users_insert_own_free
  ON public.worth_users FOR INSERT TO authenticated
  WITH CHECK (
    user_id = (SELECT auth.uid())
    AND is_premium = false
    AND premium_activated_at IS NULL
    AND premium_expires_at IS NULL
  );
CREATE POLICY worth_users_update_own
  ON public.worth_users FOR UPDATE TO authenticated
  USING (user_id = (SELECT auth.uid()))
  WITH CHECK (user_id = (SELECT auth.uid()));

-- D. Satu pesanan hanya boleh dipasangkan dengan satu kode aktivasi.
-- Hasil query sebelumnya menunjukkan seluruh order_id masih NULL, sehingga index ini tidak mengubah kode lama.
CREATE UNIQUE INDEX IF NOT EXISTS activation_codes_one_code_per_order
  ON public.activation_codes (order_id)
  WHERE order_id IS NOT NULL;

-- E. Cabut hak eksekusi dari semua overload lama fungsi aktivasi agar tidak ada jalur lama yang terbuka.
DO $functions$
DECLARE f record;
BEGIN
  FOR f IN
    SELECT p.oid::pg_catalog.regprocedure AS signature
    FROM pg_catalog.pg_proc p
    JOIN pg_catalog.pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public' AND p.proname = 'activate_worth_premium'
  LOOP
    EXECUTE pg_catalog.format(
      'REVOKE ALL ON FUNCTION %s FROM PUBLIC, anon, authenticated', f.signature
    );
  END LOOP;
END;
$functions$;

CREATE OR REPLACE FUNCTION public.activate_worth_premium(p_code text)
RETURNS jsonb
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $function$
DECLARE
  v_user_id uuid;
  v_code_id uuid;
  v_order_id uuid;
BEGIN
  v_user_id := auth.uid();
  IF v_user_id IS NULL THEN
    RETURN jsonb_build_object('success', false, 'message', 'Silakan login terlebih dahulu.');
  END IF;
  IF p_code IS NULL OR pg_catalog.btrim(p_code) = '' THEN
    RETURN jsonb_build_object('success', false, 'message', 'Kode aktivasi wajib diisi.');
  END IF;

  -- Kunci baris kode agar dua permintaan bersamaan tidak dapat memakai kode yang sama.
  SELECT ac.id, ac.order_id
    INTO v_code_id, v_order_id
  FROM public.activation_codes AS ac
  WHERE pg_catalog.upper(pg_catalog.btrim(ac.code)) = pg_catalog.upper(pg_catalog.btrim(p_code))
    AND ac.status = 'UNUSED'
  FOR UPDATE;

  IF v_code_id IS NULL THEN
    RETURN jsonb_build_object('success', false, 'message', 'Kode tidak valid atau sudah digunakan.');
  END IF;

  -- Wajib: kode terhubung ke pesanan milik akun login, nominal benar, lunas, dan diverifikasi admin.
  IF v_order_id IS NULL OR NOT EXISTS (
    SELECT 1
    FROM public.orders AS o
    WHERE o.id = v_order_id
      AND o.user_id = v_user_id
      AND o.payment_status = 'PAID'
      AND o.amount = 9900
      AND o.verified_at IS NOT NULL
  ) THEN
    RETURN jsonb_build_object(
      'success', false,
      'message', 'Pembayaran belum diverifikasi admin atau kode bukan milik pesanan akun ini.'
    );
  END IF;

  IF NOT EXISTS (SELECT 1 FROM public.worth_users AS wu WHERE wu.user_id = v_user_id) THEN
    RETURN jsonb_build_object('success', false, 'message', 'Data pengguna tidak ditemukan. Silakan login kembali.');
  END IF;

  UPDATE public.activation_codes
  SET status = 'ACTIVATED', activated_by = v_user_id, activated_at = pg_catalog.now()
  WHERE id = v_code_id AND status = 'UNUSED';
  IF NOT FOUND THEN
    RETURN jsonb_build_object('success', false, 'message', 'Kode sudah digunakan.');
  END IF;

  UPDATE public.worth_users
  SET is_premium = true,
      premium_activated_at = pg_catalog.now(),
      premium_expires_at = pg_catalog.now() + interval '1 month',
      updated_at = pg_catalog.now()
  WHERE user_id = v_user_id;

  RETURN jsonb_build_object('success', true, 'message', 'Premium berhasil diaktifkan selama 1 bulan.');
END;
$function$;

REVOKE ALL ON FUNCTION public.activate_worth_premium(text) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION public.activate_worth_premium(text) TO authenticated;

COMMIT;

-- ============================================================
-- ALUR ADMIN SETELAH UANG QRIS BENAR-BENAR DITERIMA
-- ============================================================
-- 1. Cari ID pesanan dan pastikan pemilik/nominal/status sesuai:
-- SELECT id, user_id, amount, payment_status, verified_at
-- FROM public.orders ORDER BY created_at DESC;
--
-- 2. Ganti placeholder di bawah dengan ID pesanan nyata. Jalankan hanya setelah pembayaran valid:
-- UPDATE public.orders
-- SET payment_status = 'PAID', verified_at = pg_catalog.now()
-- WHERE id = 'GANTI_ID_PESANAN'::uuid
--   AND amount = 9900 AND payment_status = 'PENDING';
-- Pastikan tepat satu baris terubah.
--
-- 3. Pasangkan SATU kode UNUSED ke pesanan yang sama:
-- UPDATE public.activation_codes
-- SET order_id = 'GANTI_ID_PESANAN'::uuid
-- WHERE code = 'GANTI_KODE_YANG_SUDAH_ADA'
--   AND status = 'UNUSED' AND order_id IS NULL;
-- Pastikan tepat satu baris terubah. Jangan menautkan kode ke pesanan akun lain.
--
-- 4. Pengguna login dengan akun pemesan, masukkan kode pada halaman Premium.
-- Jangan pernah mengubah status PAID tanpa bukti pembayaran yang sah.
