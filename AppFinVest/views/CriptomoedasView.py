from django.utils.decorators import method_decorator
from AppFinVest.decorators import login_required
from django.views import View
from django.shortcuts import render
from django.core.cache import cache
from AppFinVest.models import TabelaGlobal 

class CriptomoedasView(View):
    template_name = 'AppFinVest/pages/criptomoedas.html'

    @method_decorator(login_required)   
    def get(self, request):
        tabela_global = TabelaGlobal.get_instance()
        dados_criptomoedas = [
            {
                "nome_ativo": cripto.nome_ativo,
                "preco_atual": cripto.preco_atual,
                "capitalizacao_mercado": cripto.capitalizacao_mercado,
                "volume_24h": cripto.volume_24h,
            }
            for cripto in tabela_global.get_criptomoedas()
        ]

        criptomoedas_atualizadas = cache.get("criptomoeda_atualizadas", [])
        mensagem_atualizacao = f"As seguintes criptomoedas foram atualizadas: {', '.join(criptomoedas_atualizadas)}" if criptomoedas_atualizadas else None

        # Limpa a cache após exibir a mensagem
        cache.delete("criptomoeda_atualizadas")

        return render(request, self.template_name, {'criptomoedas': dados_criptomoedas, 'mensagem_atualizacao': mensagem_atualizacao})
