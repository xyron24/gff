"""ISO 20022 Payment Message Serializer & Parser.

Provides functions to format canonical payment transactions into valid ISO 20022
XML envelopes (pacs.008 FI-to-FI credit transfer, pain.001 customer credit transfer initiation,
and camt.053 statement reporting), as well as parse and inspect XML payloads for screening.
"""

from __future__ import annotations

import unicodedata
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union
from data.schema import PaymentTransaction


# Canonical ISO 20022 XML Namespaces
NAMESPACES = {
    "pacs008": "urn:iso:std:iso:20022:tech:xsd:pacs.008.001.08",
    "pain001": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.09",
    "camt053": "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08",
}


def format_pacs008(txn: Union[PaymentTransaction, Dict[str, Any]]) -> str:
    """Format a transaction as a pacs.008.001.08 FI-to-FI Customer Credit Transfer XML message."""
    data = txn.model_dump() if isinstance(txn, PaymentTransaction) else txn
    ts = data.get("timestamp")
    if isinstance(ts, datetime):
        ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ")
    else:
        ts_str = str(ts)

    raw_curr = data.get("currency", "USD")
    currency = raw_curr.value if hasattr(raw_curr, "value") else str(raw_curr).replace("CurrencyCode.", "")
    amount = f"{float(data.get('amount', 0.0)):.2f}"
    msg_id = f"MSG-{data.get('txn_id', '00000')}"
    e2e_id = f"E2E-{data.get('txn_id', '00000')}"

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="{NAMESPACES['pacs008']}">
  <FIToFICstmrCdtTrf>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{ts_str}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <SttlmInf>
        <SttlmMtd>CLRG</SttlmMtd>
        <ClrSys>
          <Prtry>FEDNOW</Prtry>
        </ClrSys>
      </SttlmInf>
    </GrpHdr>
    <CdtTrfTxInf>
      <PmtId>
        <EndToEndId>{e2e_id}</EndToEndId>
        <TxId>{data.get('txn_id')}</TxId>
      </PmtId>
      <PmtTpInf>
        <SvcLvl>
          <Cd>SDVA</Cd>
        </SvcLvl>
        <LclInstrm>
          <Prtry>{data.get('channel', 'ONLINE')}</Prtry>
        </LclInstrm>
        <CtgyPurp>
          <Cd>{data.get('purpose_code', 'GDDS')}</Cd>
        </CtgyPurp>
      </PmtTpInf>
      <IntrBkSttlmAmt Ccy="{currency}">{amount}</IntrBkSttlmAmt>
      <InstgAgt>
        <FinInstnId>
          <BICFI>{data.get('sender_bank_bic', 'MSTRUS33XXX')}</BICFI>
        </FinInstnId>
      </InstgAgt>
      <InstdAgt>
        <FinInstnId>
          <BICFI>{data.get('receiver_bank_bic', 'CHASUS33XXX')}</BICFI>
        </FinInstnId>
      </InstdAgt>
      <Dbtr>
        <Nm>Originator {data.get('sender_account')}</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>{data.get('sender_account')}</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <Cdtr>
        <Nm>Beneficiary {data.get('receiver_account')}</Nm>
      </Cdtr>
      <CdtrAcct>
        <Id>
          <Othr>
            <Id>{data.get('receiver_account')}</Id>
          </Othr>
        </Id>
      </CdtrAcct>
      <Purp>
        <Cd>{data.get('purpose_code', 'GDDS')}</Cd>
      </Purp>
      <RmtInf>
        <Ustrd>{data.get('remittance_info', 'Settlement')}</Ustrd>
      </RmtInf>
      <SplmtryData>
        <Envlp>
          <DeviceId>{data.get('device_id', '')}</DeviceId>
          <IpAddress>{data.get('ip_address', '')}</IpAddress>
          <MccCode>{data.get('mcc', '')}</MccCode>
        </Envlp>
      </SplmtryData>
    </CdtTrfTxInf>
  </FIToFICstmrCdtTrf>
</Document>"""
    return xml_content.strip()


def format_pain001(txn: Union[PaymentTransaction, Dict[str, Any]]) -> str:
    """Format a transaction as a pain.001.001.09 Customer Credit Transfer Initiation message."""
    data = txn.model_dump() if isinstance(txn, PaymentTransaction) else txn
    ts = data.get("timestamp")
    ts_str = ts.strftime("%Y-%m-%dT%H:%M:%SZ") if isinstance(ts, datetime) else str(ts)

    raw_curr = data.get("currency", "USD")
    currency = raw_curr.value if hasattr(raw_curr, "value") else str(raw_curr).replace("CurrencyCode.", "")
    amount = f"{float(data.get('amount', 0.0)):.2f}"
    msg_id = f"PAIN-{data.get('txn_id', '00000')}"

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="{NAMESPACES['pain001']}">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>{msg_id}</MsgId>
      <CreDtTm>{ts_str}</CreDtTm>
      <NbOfTxs>1</NbOfTxs>
      <InitgPty>
        <Nm>Client {data.get('sender_account')}</Nm>
      </InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMT-{data.get('txn_id')}</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <ReqdExctnDt>
        <Dt>{ts_str[:10]}</Dt>
      </ReqdExctnDt>
      <Dbtr>
        <Nm>Client {data.get('sender_account')}</Nm>
      </Dbtr>
      <DbtrAcct>
        <Id>
          <Othr>
            <Id>{data.get('sender_account')}</Id>
          </Othr>
        </Id>
      </DbtrAcct>
      <DbtrAgt>
        <FinInstnId>
          <BICFI>{data.get('sender_bank_bic', 'MSTRUS33XXX')}</BICFI>
        </FinInstnId>
      </DbtrAgt>
      <CdtTrfTxInf>
        <PmtId>
          <EndToEndId>E2E-{data.get('txn_id')}</EndToEndId>
        </PmtId>
        <Amt>
          <InstdAmt Ccy="{currency}">{amount}</InstdAmt>
        </Amt>
        <CdtrAgt>
          <FinInstnId>
            <BICFI>{data.get('receiver_bank_bic', 'CHASUS33XXX')}</BICFI>
          </FinInstnId>
        </CdtrAgt>
        <Cdtr>
          <Nm>Vendor {data.get('receiver_account')}</Nm>
        </Cdtr>
        <CdtrAcct>
          <Id>
            <Othr>
              <Id>{data.get('receiver_account')}</Id>
            </Othr>
          </Id>
        </CdtrAcct>
        <RmtInf>
          <Ustrd>{data.get('remittance_info', 'Commercial invoice')}</Ustrd>
        </RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>"""
    return xml_content.strip()


def parse_iso_message(xml_string: str) -> Dict[str, Any]:
    """Parse an ISO 20022 XML string into a flat dictionary extracting core transaction attributes."""
    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        raise ValueError(f"Malformed ISO 20022 XML: {e}")

    # Remove namespace prefixes for uniform extraction
    for elem in root.iter():
        if "}" in elem.tag:
            elem.tag = elem.tag.split("}", 1)[1]

    extracted: Dict[str, Any] = {
        "msg_id": root.findtext(".//MsgId"),
        "created_at": root.findtext(".//CreDtTm"),
        "txn_id": root.findtext(".//TxId") or root.findtext(".//EndToEndId"),
        "amount": None,
        "currency": None,
        "sender_account": root.findtext(".//DbtrAcct//Id//Othr//Id") or root.findtext(".//DbtrAcct//Id//IBAN"),
        "receiver_account": root.findtext(".//CdtrAcct//Id//Othr//Id") or root.findtext(".//CdtrAcct//Id//IBAN"),
        "sender_bic": root.findtext(".//InstgAgt//BICFI") or root.findtext(".//DbtrAgt//BICFI"),
        "receiver_bic": root.findtext(".//InstdAgt//BICFI") or root.findtext(".//CdtrAgt//BICFI"),
        "remittance_info": root.findtext(".//RmtInf//Ustrd"),
        "purpose_code": root.findtext(".//Purp//Cd") or root.findtext(".//CtgyPurp//Cd"),
        "device_id": root.findtext(".//SplmtryData//DeviceId"),
        "ip_address": root.findtext(".//SplmtryData//IpAddress"),
        "mcc": root.findtext(".//SplmtryData//MccCode"),
    }

    # Extract amount & currency by inspecting elements directly
    for elem in root.iter():
        if elem.tag in ["IntrBkSttlmAmt", "InstdAmt"]:
            if elem.text:
                try:
                    extracted["amount"] = float(elem.text.strip())
                except ValueError:
                    pass
            extracted["currency"] = elem.attrib.get("Ccy", "USD")
            break

    return extracted


def inspect_unicode_anomalies(text: str) -> Dict[str, Any]:
    """Inspect text for zero-width characters, homoglyphs, and mixed Unicode scripts (ATK-004 screening)."""
    if not text:
        return {"has_anomalies": False, "zero_width_count": 0, "non_ascii_count": 0, "scripts": []}

    zero_width_chars = {"\u200B", "\u200C", "\u200D", "\uFEFF", "\u202A", "\u202E"}
    zw_count = sum(1 for ch in text if ch in zero_width_chars)
    non_ascii_count = sum(1 for ch in text if ord(ch) > 127)

    scripts = set()
    for ch in text:
        if ch.isalpha():
            name = unicodedata.name(ch, "")
            script = name.split()[0] if name else "UNKNOWN"
            scripts.add(script)

    is_anomalous = zw_count > 0 or (len(scripts) > 1 and "LATIN" in scripts)

    return {
        "has_anomalies": is_anomalous,
        "zero_width_count": zw_count,
        "non_ascii_count": non_ascii_count,
        "scripts": list(scripts),
        "normalized_nfkc": unicodedata.normalize("NFKC", text),
    }
