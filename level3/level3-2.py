import requests
from Bio import SeqIO
import time
import json

# FASTA 파일 경로
fasta_file = "NC_045512.fasta"

# 염기서열 읽기
record = SeqIO.read(fasta_file, "fasta")
sequence = record.seq

print("1")
# BLAST API URL
blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

# BLAST 요청 파라미터
params = {
    "CMD": "Put",
    "PROGRAM": "blastn",
    "DATABASE": "nt",
    "QUERY": str(sequence),
    "FORMAT_TYPE": "JSON"
}

print("BLAST를 실행 중입니다...")
# BLAST 요청 보내기
response = requests.post(blast_url, data=params)
response.raise_for_status()

# 요청 ID 추출
rid = None
for line in response.text.split("\n"):
    if "RID =" in line:
        rid = line.split("=")[-1].strip()
        break

if not rid:
    raise Exception("RID를 찾을 수 없습니다.")

# 결과를 가져오기 위해 잠시 대기 및 반복 확인
result_handle = None
for _ in range(10):  # 최대 10번 반복 (조정 가능)
    print("2")
    time.sleep(30)  # 30초 대기 (조정 가능)

    # 결과를 가져오기 위한 파라미터
    result_params = {
        "CMD": "Get",
        "RID": rid,
        "FORMAT_TYPE": "JSON"
    }

    print("BLAST 결과를 가져오는 중입니다...")
    result_response = requests.get(blast_url, params=result_params)
    result_response.raise_for_status()

    # 결과가 JSON 형식인지 확인
    if result_response.headers.get('Content-Type') == 'application/json':
        result_handle = result_response.json()
        break
    else:
        print("BLAST 결과가 아직 준비되지 않았습니다. 다시 시도 중...")

if result_handle is None:
    raise Exception("BLAST 결과를 가져오지 못했습니다.")

# BLAST 결과 파싱 및 분석
print("3")
for alignment in result_handle['BlastOutput2'][0]['report']['results']['search']['hits']:
    print(f"****Alignment****")
    print(f"sequence: {alignment['description'][0]['title']}")
    print(f"length: {alignment['len']}")
    for hsp in alignment['hsps']:
        print(f"e value: {hsp['evalue']}")
        print(f"{hsp['qseq'][0:75]}...")
        print(f"{hsp['midline'][0:75]}...")
        print(f"{hsp['hseq'][0:75]}...")