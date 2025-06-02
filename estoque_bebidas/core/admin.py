from django.contrib import admin
import core.models as core_models

admin.site.register(core_models.Usuário)
admin.site.register(core_models.Fornecedor)
admin.site.register(core_models.Produto)
admin.site.register(core_models.MovimentaçãoEstoque)
