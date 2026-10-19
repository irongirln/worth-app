```sql
-- WORTH? Premium: QRIS + verifikasi pembayaran manual
-- Jalankan di Supabase Dashboard > SQL Editor.
-- Skrip ini tidak membuat kode aktivasi baru.
-- Pastikan pembayaran benar-benar diterima sebelum mengubah status menjadi PAID.

BEGIN;

-- =========================================================
-- A. BATASI AKSES LANGSUNG KE KODE AKTIVASI
-- =========================================================

REVOKE ALL ON TABLE public.activation_codes
FROM PUBLIC, anon, authenticated;

-- =========================================================
-- B. PESANAN: PENGGUNA HANYA BOLEH MELIHAT PESANANNYA SENDIRI
-- =========================================================

ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS orders_select_own ON public.orders;
DROP POLICY IF EXISTS orders_insert_own_pending ON public.orders;

REVOKE ALL ON TABLE public.orders
FROM PUBLIC, anon, authenticated;

GRANT SELECT ON TABLE public.orders TO authenticated;

GRANT INSERT (user_id, amount, payment_status, customer_email)
ON TABLE public.orders TO authenticated;

CREATE POLICY orders_select_own
ON public.orders
FOR SELECT
TO authenticated
USING (user_id = (SELECT auth.uid()));

CREATE POLICY orders_insert_own_pending
ON public.orders
FOR INSERT
TO authenticated
WITH CHECK (
    user_id = (SELECT auth.uid())
    AND amount = 9900
    AND payment_status = 'PENDING'
    AND verified_at IS NULL
);

-- =========================================================
-- C. PROFIL: PENGGUNA TIDAK BOLEH MENGUBAH STATUS PREMIUM
-- =========================================================

ALTER TABLE public.worth_users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS worth_users_select_own ON public.worth_users;
DROP POLICY IF EXISTS worth_users_insert_own_free ON public.worth_users;
DROP POLICY IF EXISTS worth_users_update_own ON public.worth_users;

ALTER TABLE public.worth_users
ALTER COLUMN is_premium SET DEFAULT false;

REVOKE ALL ON TABLE public.worth_users
FROM PUBLIC, anon, authenticated;

GRANT SELECT ON TABLE public.worth_users TO authenticated;

GRANT INSERT (
    user_id, email, name, usage_date,
    daily_checks, history, updated_at
)
ON TABLE public.worth_users TO authenticated;

GRANT UPDATE (
    email, name, usage_date,
    daily_checks, history, updated_at
)
ON TABLE public.worth_users TO authenticated;

CREATE POLICY worth_users_select_own
ON public.worth_users
FOR SELECT
TO authenticated
USING (user_id = (SELECT auth.uid()));

CREATE POLICY worth_users_insert_own_free
ON public.worth_users
FOR INSERT
TO authenticated
WITH CHECK (
    user_id = (SELECT auth.uid())
    AND is_premium = false
    AND premium_activated_at IS NULL
    AND premium_expires_at IS NULL
);

CREATE POLICY worth_users_update_own
ON public.worth_users
FOR UPDATE
TO authenticated
USING (user_id = (SELECT auth.uid()))
WITH CHECK (user_id = (SELECT auth.uid()));

-- =========================================================
-- D. SATU PESANAN HANYA BOLEH TERHUBUNG KE SATU KODE
-- =========================================================

CREATE UNIQUE INDEX IF NOT EXISTS activation_codes_one_code_per_order
ON public.activation_codes (order_id)
WHERE order_id IS NOT NULL;

-- =========================================================
-- E. HAPUS HAK EKSEKUSI FUNGSI AKTIVASI LAMA
-- =========================================================

DO $$
DECLARE
    f record;
BEGIN
    FOR f IN
        SELECT p.oid::regprocedure AS signature
        FROM pg_catalog.pg_proc p
        JOIN pg_catalog.pg_namespace n
          ON n.oid = p.pronamespace
        WHERE n.nspname = 'public'
          AND p.proname = 'activate_worth_premium'
    LOOP
        EXECUTE pg_catalog.format(
            'REVOKE ALL ON FUNCTION %s FROM PUBLIC, anon, authenticated',
            f.signature
        );
    END LOOP;
END;
$$;

-- =========================================================
-- F. FUNGSI AKTIVASI PREMIUM
-- =========================================================

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
        RETURN jsonb_build_object(
            'success', false,
            'message', 'Silakan login terlebih dahulu.'
        );
    END IF;

    IF p_code IS NULL OR pg_catalog.btrim(p_code) = '' THEN
        RETURN jsonb_build_object(
            'success', false,
            'message', 'Kode aktivasi wajib diisi.'
        );
    END IF;

    -- Kunci kode agar tidak digunakan oleh dua permintaan bersamaan.
    SELECT ac.id, ac.order_id
    INTO v_code_id, v_order_id
    FROM public.activation_codes AS ac
    WHERE pg_catalog.upper(pg_catalog.btrim(ac.code))
        = pg_catalog.upper(pg_catalog.btrim(p_code))
      AND ac.status = 'UNUSED'
    FOR UPDATE;

    IF v_code_id IS NULL THEN
        RETURN jsonb_build_object(
            'success', false,
            'message', 'Kode tidak valid atau sudah digunakan.'
        );
    END IF;

    -- Kode harus terkait pesanan milik akun ini yang sudah diverifikasi.
    IF v_order_id IS NULL OR NOT EXISTS (
        SELECT 1
        FROM public.orders AS o
        WHERE o.id = v_order_id
          AND o.user_id = v_user_id
          AND o.amount = 9900
          AND o.payment_status = 'PAID'
          AND o.verified_at IS NOT NULL
    ) THEN
        RETURN jsonb_build_object(
            'success', false,
            'message',
            'Pembayaran belum diverifikasi admin atau kode bukan milik pesanan akun ini.'
        );
    END IF;

    -- Pastikan profil pengguna tersedia.
    PERFORM 1
    FROM public.worth_users AS wu
    WHERE wu.user_id = v_user_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'message',
            'Profil pengguna tidak ditemukan. Silakan login kembali.'
        );
    END IF;

    -- Aktifkan kode hanya jika masih UNUSED.
    UPDATE public.activation_codes
    SET status = 'ACTIVATED',
        activated_by = v_user_id,
        activated_at = pg_catalog.now()
    WHERE id = v_code_id
      AND status = 'UNUSED';

    IF NOT FOUND THEN
        RETURN jsonb_build_object(
            'success', false,
            'message', 'Kode sudah digunakan.'
        );
    END IF;

    -- Aktifkan Premium selama satu bulan.
    UPDATE public.worth_users
    SET is_premium = true,
        premium_activated_at = pg_catalog.now(),
        premium_expires_at = pg_catalog.now() + interval '1 month',
        updated_at = pg_catalog.now()
    WHERE user_id = v_user_id;

    RETURN jsonb_build_object(
        'success', true,
        'message', 'Premium berhasil diaktifkan selama 1 bulan.'
    );
END;
$function$;

REVOKE ALL ON FUNCTION public.activate_worth_premium(text)
FROM PUBLIC, anon;

GRANT EXECUTE ON FUNCTION public.activate_worth_premium(text)
TO authenticated;

COMMIT;

-- =========================================================
-- G. PEMERIKSAAN PESANAN
-- =========================================================

SELECT
    o.id,
    o.user_id,
    o.amount,
    o.payment_status,
    o.verified_at,
    ac.code,
    ac.status AS status_kode
FROM public.orders AS o
LEFT JOIN public.activation_codes AS ac
    ON ac.order_id = o.id
ORDER BY o.created_at DESC;
```
