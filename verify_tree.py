import os, sys
ROOT=os.path.dirname(os.path.abspath(__file__))
expected=[
"backend/app/main.py","backend/app/models.py","backend/app/routers/setup.py",
"frontend/src/App.tsx","frontend/src/api.ts","run_backend.bat","run_frontend.bat"
]
missing=[p for p in expected if not os.path.exists(os.path.join(ROOT,p))]
print("verify_tree")
if missing:
  print("MISSING:"); [print(" -",m) for m in missing]; sys.exit(1)
print("OK")
