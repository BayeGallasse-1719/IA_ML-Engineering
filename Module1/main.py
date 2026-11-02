from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from immoanalyse.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline(ROOT)
    print("Pipeline ImmoAnalyse terminé.")
    print(f"Enregistrements traités : {len(result)}")
    print(f"Conformes : {(result.decision == 'conforme').sum()}")
    print(f"Avec avertissement : {(result.decision == 'avertissement').sum()}")
    print(f"En quarantaine : {(result.decision == 'quarantaine').sum()}")
    print(f"Résultats : {ROOT / 'sortie'}")
