services:
  - type: worker
    name: F.R.I.D.A.Y.
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
