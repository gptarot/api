# GPTarot - A Tarot Reader And Numerology Website (Powered By AI)

<p align='center'>
<img width=100 src='https://assets.coingecko.com/coins/images/17881/large/tarot-200px.png?1629704943'>
</p>

## Development

### API

1. Install `uv`: https://docs.astral.sh/uv
2. Change directory to `backend`.
2. Setup `OPENAI_API_KEY` in `.env`.
3. Install dependencies:

    ```bash
    uv sync --all-groups --all-extras
    ```

4. Start the server:

    ```bash
    uv run python3 src/gptarot/app.py
    ```

5. Open [http://localhost:8000/docs](http://localhost:8000/docs) and you can see the FastAPI documentation.
