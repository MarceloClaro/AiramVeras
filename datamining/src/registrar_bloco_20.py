import sys
import os

sys.path.append(os.path.abspath('datamining/src'))
from gerar_dossie_3ano_1000_laudas_multidisciplinar import register_block_ledger

hash_pdf = "e7e63d89e72262756eed29127b9d9eee6961bc7cc323eb0242035d5b501c3d56"
register_block_ledger(hash_pdf)
