# FindMyStuff API

A lightweight Flask API for tracking items stored in bins, with tag-based searching.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The server runs on `http://localhost:5000`.

## Data model

- **Bin**: `{ "id": "1234", "location": "Garage shelf", "tags": ["tools"] }`
- **Item**: `{ "id": "hammer", "name": "Claw Hammer", "bin_id": "1234", "tags": ["tools", "metal"] }`

## API endpoints

### Health check

- `GET /health`

### Bins

- `GET /bins`
  - Optional query param `tag` to filter by tag.
- `POST /bins`
  - Body:
    ```json
    {
      "id": "1234",
      "location": "Garage shelf",
      "tags": ["tools", "heavy"]
    }
    ```
- `GET /bins/<bin_id>`
- `PUT /bins/<bin_id>`
  - Body can include `location` and/or `tags`.
- `DELETE /bins/<bin_id>`
  - Fails if the bin contains items.
- `GET /bins/<bin_id>/items`
  - Optional query param `tag` to filter items in the bin.

### Items

- `GET /items`
  - Optional query param `tag` to filter by tag.
- `POST /items`
  - Body:
    ```json
    {
      "id": "hammer",
      "name": "Claw Hammer",
      "bin_id": "1234",
      "tags": ["tools", "metal"]
    }
    ```
- `GET /items/<item_id>`
- `PUT /items/<item_id>`
  - Body can include `name`, `bin_id`, and/or `tags`.
- `DELETE /items/<item_id>`

## Notes

- Bin IDs must be 4-digit strings.
- Tags must be a list of strings.
- Delete items or move them to a different bin before deleting a bin.
