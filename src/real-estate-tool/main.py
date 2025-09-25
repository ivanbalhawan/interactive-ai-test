import uvicorn
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse

from graph import invoke_graph
from models import UserInput


app = FastAPI()


@app.post("/generate_property_listing")
async def generate_property_listing(request: Request):
    data = await request.json()
    user_input = UserInput(**data)
    with open("input.json", "w") as file:
        file.write(user_input.model_dump_json())
    result = invoke_graph(user_input)
    result_html = result.to_html()
    with open("output.html", "w") as file:
        file.write(result_html)
    return HTMLResponse(result_html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
