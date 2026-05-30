from decimal import Decimal

def calcular_cronograma_compra_inteligente(simulacion):
    """
    Motor de Ingeniería Económica para Compra Inteligente.
    Calcula: TEM, Gracia, Método Francés con Valor Residual, VAN, TIR y TCEA real.
    """
    # 1. Conversión de Moneda Base
    precio_auto = simulacion.vehiculo.precio_base
    if simulacion.moneda == 'PEN':
        precio_base_moneda = precio_auto * simulacion.tipo_cambio
    else:
        precio_base_moneda = precio_auto
        
    # 2. Descomposición de la Estructura de Capital
    cuota_inicial = precio_base_moneda * (simulacion.cuota_inicial_porcentaje / Decimal('100.00'))
    monto_financiar = precio_base_moneda - cuota_inicial
    cuota_balon = monto_financiar * (simulacion.cuota_balon_porcentaje / Decimal('100.00'))
    
    # 3. Conversión de Tasas SBS (De Anual a Mensual Efectiva)
    tea = float(simulacion.banco.tea) / 100.0
    tem_flotante = (1.0 + tea) ** (1.0 / 12.0) - 1.0
    tem = Decimal(str(tem_flotante))
    
    # Tasas de Seguros Prorrateadas
    tasa_desg = Decimal(str(float(simulacion.banco.tasa_desgravamen) / 100.0))
    tasa_veh_mes = Decimal(str((float(simulacion.banco.tasa_seguro_vehicular) / 100.0) / 12.0))
    portes = simulacion.banco.comision_portes
    
    cronograma = []
    saldo_inicial = monto_financiar
    
    # Periodo 0: Desembolso Inicial
    cronograma.append({
        'periodo': 0,
        'saldo_inicial': Decimal('0.00'),
        'cuota_pura': Decimal('0.00'),
        'interes': Decimal('0.00'),
        'amortizacion': Decimal('0.00'),
        'desgravamen': Decimal('0.00'),
        'seg_vehicular': Decimal('0.00'),
        'portes': Decimal('0.00'),
        'cuota_total': Decimal('0.00'),
        'saldo_final': saldo_inicial
    })
    
    # 4. Fase A: Procesamiento de Periodos de Gracia Diferidos
    for p in range(1, simulacion.meses_gracia + 1):
        interes_mes = saldo_inicial * tem
        desg_mes = saldo_inicial * tasa_desg
        veh_mes = precio_base_moneda * tasa_veh_mes
        
        if simulacion.tipo_gracia == 'TOTAL':
            # Gracia Total: No hay cuota pura, el interés se capitaliza al saldo vivo
            cuota_pura = Decimal('0.00')
            amortizacion = Decimal('0.00')
            saldo_final = saldo_inicial + interes_mes
        else:  # PARCIAL
            # Gracia Parcial: Se paga el interés generado, el capital se mantiene estático
            cuota_pura = interes_mes
            amortizacion = Decimal('0.00')
            saldo_final = saldo_inicial
            
        cuota_total = cuota_pura + desg_mes + veh_mes + portes
        
        cronograma.append({
            'periodo': p,
            'saldo_inicial': saldo_inicial,
            'cuota_pura': cuota_pura,
            'interes': interes_mes,
            'amortizacion': amortizacion,
            'desgravamen': desg_mes,
            'seg_vehicular': veh_mes,
            'portes': portes,
            'cuota_total': cuota_total,
            'saldo_final': saldo_final
        })
        saldo_inicial = saldo_final

    # 5. Fase B: Cálculo de Renta Constante (Método Francés con Cuota Balón)
    n_amortizacion = simulacion.plazo_meses - simulacion.meses_gracia
    
    if n_amortizacion > 0:
        s0 = float(saldo_inicial)
        b = float(cuota_balon)
        j = float(tem)
        
        # Ecuación de Anualidades con Valor Residual Acoplado
        factor = (1.0 + j) ** n_amortizacion
        r_pura_flotante = (j * s0 * factor - j * b) / (factor - 1.0)
        r_pura = Decimal(str(r_pura_flotante))
    else:
        r_pura = Decimal('0.00')

    # 6. Fase C: Amortización Ordinaria Regular
    for p in range(simulacion.meses_gracia + 1, simulacion.plazo_meses + 1):
        interes_mes = saldo_inicial * tem
        desg_mes = saldo_inicial * tasa_desg
        veh_mes = precio_base_moneda * tasa_veh_mes
        
        if p == simulacion.plazo_meses:
            # En el último mes se amortiza el saldo ordinario + la cuota balón pactada
            cuota_pura = r_pura + cuota_balon
            amortizacion = cuota_pura - interes_mes
            saldo_final = Decimal('0.00')
        else:
            cuota_pura = r_pura
            amortizacion = cuota_pura - interes_mes
            saldo_final = saldo_inicial - amortizacion
            
        cuota_total = cuota_pura + desg_mes + veh_mes + portes
        
        cronograma.append({
            'periodo': p,
            'saldo_inicial': saldo_inicial,
            'cuota_pura': cuota_pura,
            'interes': interes_mes,
            'amortizacion': amortizacion,
            'desgravamen': desg_mes,
            'seg_vehicular': veh_mes,
            'portes': portes,
            'cuota_total': cuota_total,
            'saldo_final': saldo_final
        })
        saldo_inicial = saldo_final

    # 7. Fase D: Evaluación de Indicadores de Rentabilidad y Costo Efectivo (VAN, TIR, TCEA)
    # Construcción del vector de flujos netos desde la perspectiva del cliente
    flujos_tcea = [float(monto_financiar)] + [-float(x['cuota_total']) for x in cronograma[1:]]
    
    # Algoritmo de Bisección Numérica para capturar la raíz de la TIR Mensual
    low, high = -0.99, 4.0
    tir_mensual = 0.0
    for _ in range(100):
        mid = (low + high) / 2.0
        van_aux = sum(f / ((1.0 + mid) ** t) for t, f in enumerate(flujos_tcea))
        if abs(van_aux) < 1e-5:
            tir_mensual = mid
            break
        if van_aux > 0:
            high = mid  # Exceso de descuento, disminuir tasa
        else:
            low = mid   # Defecto de descuento, aumentar tasa
    else:
        tir_mensual = (low + high) / 2.0
        
    # Capitalización de la TCEA Real del contrato
    tcea_porcentaje = ((1.0 + tir_mensual) ** 12) - 1.0
    
    # Flujos para evaluación del VAN del banco inversionista
    flujos_banco = [-float(monto_financiar)] + [float(x['cuota_total']) for x in cronograma[1:]]
    van_banco = sum(f / ((1.0 + float(tem)) ** t) for t, f in enumerate(flujos_banco))
    tir_banco_anual = tir_mensual * 12  # TIR Nominal anualizada corporativa

    return {
        'cronograma': cronograma,
        'tcea': Decimal(str(tcea_porcentaje * 100)),
        'van': Decimal(str(van_banco)),
        'tir': Decimal(str(tir_banco_anual * 100)),
        'monto_financiar': monto_financiar,
        'cuota_inicial': cuota_inicial,
        'cuota_balon': cuota_balon,
        'precio_base_moneda': precio_base_moneda
    }