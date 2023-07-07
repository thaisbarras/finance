from datetime import datetime, timedelta
from io import BytesIO
import os
import re
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.conf import settings
from extrato.models import Valores
from perfil.models import Categoria, Conta
from django.contrib import messages
from django.contrib.messages import constants
from django.template.loader import render_to_string
from weasyprint import HTML

def novo_valor(request):
    if request.method == "GET":
        contas = Conta.objects.all()
        categorias = Categoria.objects.all() 
        return render(request, 'novo_valor.html', {'contas': contas, 'categorias': categorias})
    elif request.method == "POST":
        valor = request.POST.get('valor')
        categoria = request.POST.get('categoria')
        descricao = request.POST.get('descricao')
        data = request.POST.get('data')
        conta = request.POST.get('conta')
        tipo = request.POST.get('tipo')
        
        valores = Valores(
            valor=valor,
            categoria_id=categoria,
            descricao=descricao,
            data=data,
            conta_id=conta,
            tipo=tipo,
        )

        valores.save()

        conta = Conta.objects.get(id=conta)

        if tipo == 'E':
            conta.valor += int(valor)
            messages.add_message(request, constants.SUCCESS, 'Entrada cadastrada com sucesso')
            
        else:
            conta.valor -= int(valor)
            messages.add_message(request, constants.SUCCESS, 'Saída cadastrada com sucesso')


        conta.save()

        
        return redirect('/extrato/novo_valor')
    
def view_extrato(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    conta_get = request.GET.get('conta')
    categoria_get = request.GET.get('categoria')
    reset_get = request.GET.get('resetar')
    periodo_get = request.GET.get('periodo')

           
    valores = Valores.objects.filter(data__month=datetime.now().month)

    if conta_get:
        valores = valores.filter(conta__id=conta_get)
    if categoria_get:
        valores = valores.filter(categoria__id=categoria_get)
    if reset_get:
        return redirect(view_extrato)
    if periodo_get:
        #valores = Valores.objects.filter(data=datetime.today()-timedelta(days=7))
        pass
    

    
    return render(request, 'view_extrato.html', {'valores': valores, 'contas': contas, 'categorias': categorias})        

def exportar_pdf(request):
    valores = Valores.objects.filter(data__month=datetime.now().month)
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()
    
    path_template = os.path.join(settings.BASE_DIR, 'templates/partials/extrato.html')
    #biblioteca que salva o documento na máquina do usuario
    #o objeto fica em memória RAM e não ocupa disco do servidor
    path_output = BytesIO()

    template_render = render_to_string(path_template, {'valores': valores, 'contas': contas, 'categorias': categorias})
    HTML(string=template_render).write_pdf(path_output)

    #voltando o ponteiro para o início do arquivo
    path_output.seek(0)
    

    return FileResponse(path_output, filename="extrato.pdf")