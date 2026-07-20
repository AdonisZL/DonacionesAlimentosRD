PS C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD> mkdir frontend

目录: C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD
Mode                 LastWriteTime         Length Name

---

d-----         2026/7/10     10:34                frontend

PS C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD> mkdir backend

目录: C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD
Mode                 LastWriteTime         Length Name

---

d-----         2026/7/10     10:34                backend

PS C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD> cd frontend
PS C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD\frontend> npm create vite@latest .

> npx
> create-vite .

│
◇  Select a framework:
│  React
│
◇  Select a variant:
│  JavaScript
│
◇  Which linter to use?
│  Oxlint
│
◇  Install with npm and start now?
│  Yes
│
◇  Scaffolding project in C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD\frontend...
│
◇  Installing dependencies with npm...

added 24 packages, and audited 25 packages in 4s

9 packages are looking for funding
run `npm fund` for details

found 0 vulnerabilities
│
◇  Starting dev server...

> frontend@0.0.0 dev
> vite

VITE v8.1.4  ready in 603 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
➜  press h + enter to show help

退出服务器：
Ctrl + C

backend

cd C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD\backend
激活虚拟环境：
venv\Scripts\activate
退出虚拟环境：
deactivate

安装FastAPI：
pip install fastapi
pip install uvicorn
pip install sqlalchemy
pip install psycopg2-binary
pip install python-dotenv

Fronend 前端：
cd C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD\frontend
npm run dev

Backend后端打开网址：
cd C:\Users\Adonl\Desktop\Tesis\DonacionesAlimentosRD\backend
venv\Scripts\activate
uvicorn app.main:app --reload
或者：.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

Swagger 自动生成
http://127.0.0.1:8000/docs

PostgreSQL
User:
postgres

Password:
9709



Cuentas de prueba / 测试账号
Contraseña común / 通用密码: DemoRD2026! (mínimo 10 caracteres) / （至少10位）

Rol	Correo	Qué puedes probar
🏦 Banco	banco.demo@ejemplo.com	Todo: inventario, alertas, emparejamientos, reportes y reporte fiscal
🏪 Donante	donante.demo@ejemplo.com	Sus lotes + buscar receptores
🍽️ Receptor 1	comedor.demo@ejemplo.com	Recibe emparejamientos (tiene cadena de frío)
🤝 Receptor 2	fundacion.demo@ejemplo.com	Receptor sin cadena de frío




Cuenta de administrador / 管理员账号
admin.demo@ejemplo.com / AdminRD2026! (creada con scripts/crear_admin.py, no por API por seguridad). / 通过脚本创建，非 API。