REVOKE SELECT ON TABLE public.interacoes_app FROM anon;
GRANT SELECT (imovel_id, tipo_interacao, created_at)
  ON TABLE public.interacoes_app
  TO anon;

REVOKE SELECT ON TABLE public.favoritos FROM anon;
GRANT SELECT (imovel_id, created_at) ON TABLE public.favoritos TO anon;

DROP POLICY IF EXISTS "Painel web lê favoritos sem IDs de usuário" ON public.favoritos;

CREATE POLICY "Painel web lê favoritos sem IDs de usuário"
  ON public.favoritos
  FOR SELECT
  TO anon
  USING (true);
