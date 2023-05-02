""" Sites helper functions."""
from datetime import datetime


def create_transaction(trx):
    transaction = {
        "fecha_evento": str(trx["metadata"]["fecha_evento"]),
        "fecha_punto_venta": str(trx["metadata"]["fecha_evento"]),
        "id_transaccion": trx["metadata"]["id_transaccion"],
        "metadata": {
            "id_sistema": trx["metadata"]["id_sistema"],
            "id_transaccion_original": trx["metadata"][
                "id_transaccion_original"
            ],
            "id_transaccion": trx["metadata"]["id_transaccion"],
            "tipo_documento": trx["metadata"]["tipo_documento"],
            "tipo_evento": trx["metadata"]["tipo_evento"],
            "id_comercio": trx["metadata"]["id_comercio"],
            "id_eds": trx["metadata"]["id_eds"],
            "fecha_evento": trx["metadata"]["fecha_evento"],
            "total_venta": trx["metadata"]["total_venta"],
            "total_venta_con_descuento": trx["metadata"][
                "total_venta_con_descuento"
            ],
            "monto_descuento_total": trx["metadata"]["monto_descuento_total"],
            "medio_de_pago": trx["metadata"]["medio_de_pago"],
            "id_autorizador": trx["metadata"]["medio_de_pago"],
            "codigo_producto": trx["metadata"]["codigo_producto"],
            "programas_canjeados": trx["metadata"]["programas_canjeados"],
            "tipo_operacion_comercial": trx["metadata"][
                "tipo_operacion_comercial"
            ]
            if "tipo_operacion_comercial" in trx["metadata"]
            else "",
            "agregaciones_sap": {},
            "fecha_insercion": trx["metadata"]["fecha_insercion"],
        },
    }

    # Se registran las fecha de auditoria.

    transaction["metadata"][
        "fecha_actualizacion"
    ] = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    transaction["fecha_carga_elastic"] = "FECHA#NONE"
    transaction["comercio"] = trx["metadata"]["id_comercio"]
    transaction["eds"] = str(trx["metadata"]["id_eds"])
    try:
        if trx["metadata"]["id_comercio"] in ["PRONTO", "PUNTO"]:
            transaction["metadata"]["monto_venta"] = trx["metadata"]["total_venta"]
            transaction["metadata"]["monto_total"] = trx["metadata"]["total_venta_con_descuento"]
    except Exception:
        pass
    return transaction


def add_promociones_no_punto(
    promociones,
    metadata,
    monto_abono_negocio_gral,
    monto_aporte_descto_gral,
    monto_abono_negocio_fid,
    monto_aporte_descto_fid,
    monto_fijo_al_cierre,
    monto_abono_negocio,
):
    if (
        "datosCupon" in promociones
        and "tipoPrograma" in promociones["datosCupon"]
        and "tipoAbonoNegocio" in promociones["datosCupon"]
    ):
        monto_fijo_al_cierre += (
            promociones["datosCupon"]["valorMontoFijo_alCierre"]
            if "valorMontoFijo_alCierre" in promociones["datosCupon"]
            else 0
        )
        if promociones["datosCupon"]["tipoAbonoNegocio"] == "DCTO_TOTAL":
            monto_abono_negocio = (
                promociones["valorDescuentoTotal"]
                * promociones["datosCupon"]["aporteDescuento"]
                / 100
                if "valorDescuentoTotal" in promociones
                and "aporteDescuento" in promociones["datosCupon"]
                else 0
            )
        elif promociones["datosCupon"]["tipoAbonoNegocio"] == "MONTO_FIJO":
            monto_abono_negocio = (
                promociones["datosCupon"]["valorMontoFijo_AlDia"]
                if "valorMontoFijo_AlDia" in promociones["datosCupon"]
                else 0
            )
        elif promociones["datosCupon"]["tipoAbonoNegocio"] == "TOTAL":
            monto_abono_negocio = (
                promociones["valorDescuentoTotal"]
                if "valorDescuentoTotal" in promociones
                else 0
            )
        if promociones["datosCupon"]["tipoPrograma"] == "FIDELIDAD":
            monto_abono_negocio_fid += monto_abono_negocio
        else:
            monto_abono_negocio_gral += monto_abono_negocio
    else:
        if metadata["id_comercio"] != "COMBUSTIBL":
            monto_abono_negocio_gral += 0
        else:
            monto_abono_negocio_gral += (
                promociones["valorDescuentoTotal"]
                if "valorDescuentoTotal" in promociones
                else 0
            )
    return (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
        monto_abono_negocio,
    )


def add_promociones_punto(
    promociones,
    monto_abono_negocio,
    monto_fijo_al_cierre,
    monto_abono_negocio_fid,
    monto_abono_negocio_gral,
    metadata,
):
    if (
        "datosCupon" in promociones
        and "tipoPrograma" in promociones["datosCupon"]
        and "tipoAbonoNegocio" in promociones["datosCupon"]
    ):
        monto_fijo_al_cierre += (
            promociones["datosCupon"]["valorMontoFijo_alCierre_Punto"]
            if "valorMontoFijo_alCierre_Punto" in promociones["datosCupon"]
            else 0
        )
        if promociones["datosCupon"]["tipoAbonoNegocio"] == "DCTO_TOTAL":
            monto_abono_negocio = (
                promociones["valorDescuentoTotal"]
                * promociones["datosCupon"]["aporteDescuento_Punto"]
                / 100
                if "valorDescuentoTotal" in promociones
                and "aporteDescuento_Punto" in promociones["datosCupon"]
                else 0
            )
        elif promociones["datosCupon"]["tipoAbonoNegocio"] == "MONTO_FIJO":
            monto_abono_negocio = (
                promociones["datosCupon"]["valorMontoFijo_AlDia_Punto"]
                if "valorMontoFijo_AlDia_Punto" in promociones["datosCupon"]
                else 0
            )
        elif promociones["datosCupon"]["tipoAbonoNegocio"] == "TOTAL":
            monto_abono_negocio = (
                promociones["valorDescuentoTotal"]
                if "valorDescuentoTotal" in promociones
                else 0
            )
        if promociones["datosCupon"]["tipoPrograma"] == "FIDELIDAD":
            monto_abono_negocio_fid += monto_abono_negocio
        else:
            monto_abono_negocio_gral += monto_abono_negocio
    else:
        if metadata["id_comercio"] != "COMBUSTIBL":
            monto_abono_negocio_gral += 0
        else:
            monto_abono_negocio_gral += (
                promociones["valorDescuentoTotal"]
                if "valorDescuentoTotal" in promociones
                else 0
            )
    return (
        monto_abono_negocio,
        monto_fijo_al_cierre,
        monto_abono_negocio_fid,
        monto_abono_negocio_gral,
    )


def calculate_monto_aporte_no_punto(metadata):
    """Funcion que calcula el monto aporte en base a la informacion de la transaccion.

    :Args
        metadata: Metadata de la transaccion.
    :Returns
        Retorna un integer con el monto total.
    """
    monto_abono_negocio_gral = 0
    monto_aporte_descto_gral = 0
    monto_abono_negocio_fid = 0
    monto_aporte_descto_fid = 0
    monto_fijo_al_cierre = 0
    monto_abono_negocio = 0
    promociones_canjeadas = (
        metadata["programas_canjeados"]
        if "programas_canjeados" in metadata
        else []
    )
    for promociones in promociones_canjeadas:
        (
            monto_abono_negocio_gral,
            monto_aporte_descto_gral,
            monto_abono_negocio_fid,
            monto_aporte_descto_fid,
            monto_fijo_al_cierre,
            monto_abono_negocio,
        ) = add_promociones_no_punto(
            promociones,
            metadata,
            monto_abono_negocio_gral,
            monto_aporte_descto_gral,
            monto_abono_negocio_fid,
            monto_aporte_descto_fid,
            monto_fijo_al_cierre,
            monto_abono_negocio,
        )
    return (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
    )


def calculate_monto_aporte_punto(metadata):
    """Funcion que calcula el monto aporte en base a la informacion de la transaccion.

    :Args
        metadata: Metadata de la transaccion.
    :Returns
        Retorna un integer con el monto total.
    """
    # monto_abono_negocio_gral, monto_aporte_descto_gral, monto_abono_negocio_fid, monto_aporte_descto_fid
    monto_abono_negocio_gral = 0
    monto_aporte_descto_gral = 0
    monto_abono_negocio_fid = 0
    monto_aporte_descto_fid = 0
    monto_fijo_al_cierre = 0
    monto_abono_negocio = 0
    promociones_canjeadas = (
        metadata["programas_canjeados"]
        if "programas_canjeados" in metadata
        else []
    )
    for promociones in promociones_canjeadas:
        (
            monto_abono_negocio,
            monto_fijo_al_cierre,
            monto_abono_negocio_fid,
            monto_abono_negocio_gral,
        ) = add_promociones_punto(
            promociones,
            monto_abono_negocio,
            monto_fijo_al_cierre,
            monto_abono_negocio_fid,
            monto_abono_negocio_gral,
            metadata,
        )
    return (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
    )


def calculate_monto_aporte(metadata):
    """Funcion que calcula el monto aporte en base a la informacion de la transaccion.

    :Args
        metadata: Metadata de la transaccion.
    :Returns
        Retorna un integer con el monto total.
    """
    # monto_abono_negocio_gral, monto_aporte_descto_gral, monto_abono_negocio_fid, monto_aporte_descto_fid
    monto_abono_negocio_gral = 0
    monto_aporte_descto_gral = 0
    monto_abono_negocio_fid = 0
    monto_aporte_descto_fid = 0
    monto_fijo_al_cierre = 0
    monto_abono_negocio = 0
    if (
        metadata["id_sistema"] == "fidelidad"
        and metadata["id_comercio"] != "PUNTO"
    ):
        promociones_canjeadas = (
            metadata["programas_canjeados"]
            if "programas_canjeados" in metadata
            else []
        )
        for promociones in promociones_canjeadas:
            (
                monto_abono_negocio_gral,
                monto_aporte_descto_gral,
                monto_abono_negocio_fid,
                monto_aporte_descto_fid,
                monto_fijo_al_cierre,
                monto_abono_negocio,
            ) = add_promociones_no_punto(
                promociones,
                metadata,
                monto_abono_negocio_gral,
                monto_aporte_descto_gral,
                monto_abono_negocio_fid,
                monto_aporte_descto_fid,
                monto_fijo_al_cierre,
                monto_abono_negocio,
            )
    if (
        metadata["id_sistema"] == "fidelidad"
        and metadata["id_comercio"] == "PUNTO"
    ):
        promociones_canjeadas = (
            metadata["programas_canjeados"]
            if "programas_canjeados" in metadata
            else []
        )
        for promociones in promociones_canjeadas:
            (
                monto_abono_negocio,
                monto_fijo_al_cierre,
                monto_abono_negocio_fid,
                monto_abono_negocio_gral,
            ) = add_promociones_punto(
                promociones,
                monto_abono_negocio,
                monto_fijo_al_cierre,
                monto_abono_negocio_fid,
                monto_abono_negocio_gral,
                metadata,
            )
    return (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
    )


def create_agregaciones_sap(trx, agg_type):
    if agg_type == "PUNTO":
        (
            monto_abono_negocio_gral,
            monto_aporte_descto_gral,
            monto_abono_negocio_fid,
            monto_aporte_descto_fid,
            monto_fijo_al_cierre,
        ) = calculate_monto_aporte_punto(trx["metadata"])
    else:
        (
            monto_abono_negocio_gral,
            monto_aporte_descto_gral,
            monto_abono_negocio_fid,
            monto_aporte_descto_fid,
            monto_fijo_al_cierre,
        ) = calculate_monto_aporte_no_punto(trx["metadata"])
    agregaciones_sap = {}
    agregaciones_sap[
        "monto_abono_negocio_gral"
    ] = monto_abono_negocio_gral
    agregaciones_sap[
        "monto_aporte_descto_gral"
    ] = monto_aporte_descto_gral
    agregaciones_sap[
        "monto_abono_negocio_fid"
    ] = monto_abono_negocio_fid
    agregaciones_sap[
        "monto_aporte_descto_fid"
    ] = monto_aporte_descto_fid
    agregaciones_sap[
        "monto_fijo_al_cierre"
    ] = monto_fijo_al_cierre
    return agregaciones_sap


def create_transaction_fidelidad_t_muevo(trx):
    transaction = create_transaction(trx)
    transaction["PK"] = (
        "FIDELIDAD#T#" + transaction["metadata"]["id_transaccion"]
    )
    transaction["SK"] = trx["SK"]
    (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
    ) = calculate_monto_aporte(trx["metadata"])
    transaction["metadata"]["agregaciones_sap"][
        "monto_abono_negocio_gral"
    ] = monto_abono_negocio_gral
    transaction["metadata"]["agregaciones_sap"][
        "monto_aporte_descto_gral"
    ] = monto_aporte_descto_gral
    transaction["metadata"]["agregaciones_sap"][
        "monto_abono_negocio_fid"
    ] = monto_abono_negocio_fid
    transaction["metadata"]["agregaciones_sap"][
        "monto_aporte_descto_fid"
    ] = monto_aporte_descto_fid
    transaction["metadata"]["agregaciones_sap"][
        "monto_fijo_al_cierre"
    ] = monto_fijo_al_cierre

    transaction["metadata"]["agregaciones_sap_no_punto"] = (
        create_agregaciones_sap(trx, "NO_PUNTO")
    )
    transaction["metadata"]["agregaciones_sap_punto"] = (
        create_agregaciones_sap(trx, "PUNTO")
    )
    return transaction


def create_transaction_fidelidad_t_no_muevo(trx):
    transaction = create_transaction(trx)
    transaction["PK"] = (
        "FIDELIDAD#T#" + transaction["metadata"]["id_transaccion"]
    )
    transaction["SK"] = trx["SK"]
    (
        monto_abono_negocio_gral,
        monto_aporte_descto_gral,
        monto_abono_negocio_fid,
        monto_aporte_descto_fid,
        monto_fijo_al_cierre,
    ) = calculate_monto_aporte(trx["metadata"])
    transaction["metadata"]["agregaciones_sap"][
        "monto_abono_negocio_gral"
    ] = monto_abono_negocio_gral
    transaction["metadata"]["agregaciones_sap"][
        "monto_aporte_descto_gral"
    ] = monto_aporte_descto_gral
    transaction["metadata"]["agregaciones_sap"][
        "monto_abono_negocio_fid"
    ] = monto_abono_negocio_fid
    transaction["metadata"]["agregaciones_sap"][
        "monto_aporte_descto_fid"
    ] = monto_aporte_descto_fid
    transaction["metadata"]["agregaciones_sap"][
        "monto_fijo_al_cierre"
    ] = monto_fijo_al_cierre

    transaction["metadata"]["agregaciones_sap_no_punto"] = (
        create_agregaciones_sap(trx, "NO_PUNTO")
    )

    transaction["metadata"]["agregaciones_sap_punto"] = (
        create_agregaciones_sap(trx, "PUNTO")
    )

    return transaction
