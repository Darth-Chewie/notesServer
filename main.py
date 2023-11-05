from flask import Flask, jsonify, request, abort
import json
import os

app = Flask(__name__)

# File where notes will be stored
NOTES_FILE = 'notes.json'

def read_notes_from_file():
    if not os.path.exists(NOTES_FILE):
        return {}
    with open(NOTES_FILE, 'r') as file:
        return json.load(file)

def write_notes_to_file(notes):
    with open(NOTES_FILE, 'w') as file:
        json.dump(notes, file, indent=4)

def get_next_note_id(notes):
    if notes:
        return max(int(key) for key in notes.keys()) + 1
    return 1

@app.route('/v1/notes', methods=['POST'])
def create_note():
    notes = read_notes_from_file()
    note_id_counter = get_next_note_id(notes)

    note = request.get_json()

    if not note or not note.get('title') or not note.get('content'):
        abort(400, 'Title and content are required.')

    note['id'] = note_id_counter
    notes[note_id_counter] = note

    write_notes_to_file(notes)

    return jsonify(note), 201

@app.route('/v1/notes', methods=['GET'])
def get_notes():
    notes = read_notes_from_file()
    return jsonify(list(notes.values())), 200

@app.route('/v1/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    notes = read_notes_from_file()

    note = notes.get(str(note_id))
    if not note:
        abort(404, 'Note not found.')

    return jsonify(note), 200

@app.route('/v1/notes/<int:note_id>', methods=['PUT', 'PATCH'])
def update_note(note_id):
    notes = read_notes_from_file()

    if str(note_id) not in notes:
        abort(404, 'Note not found.')

    update_data = request.get_json()
    if not update_data:
        abort(400, 'JSON body is required.')

    if request.method == 'PATCH':
        notes[str(note_id)].update(update_data)
    else:
        update_data['id'] = note_id
        notes[str(note_id)] = update_data

    write_notes_to_file(notes)

    return jsonify(notes[str(note_id)]), 200

@app.route('/v1/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    notes = read_notes_from_file()

    if str(note_id) in notes:
        del notes[str(note_id)]
        write_notes_to_file(notes)
        return jsonify({'message': 'Note deleted successfully.'}), 200
    else:
        abort(404, 'Note not found.')

# Error handlers remain unchanged...

if __name__ == '__main__':
    app.run(debug=True)
