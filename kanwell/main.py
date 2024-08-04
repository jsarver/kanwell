from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Protocol
from nicegui import ui
from cherwell import load_records, update_records


class Item(Protocol):
    title: str


dragged: Optional[card] = None


class column(ui.column):

    def __init__(self, name: str, on_drop: Optional[Callable[[Item, str], None]] = None) -> None:
        super().__init__()
        with self.classes('bg-blue-grey-2 w-60 p-4 rounded shadow-2'):
            ui.label(name).classes('text-bold ml-1')
        self.name = name
        self.on('dragover.prevent', self.highlight)
        self.on('dragleave', self.unhighlight)
        self.on('drop', self.move_card)
        self.on_drop = on_drop
        # self.on('click', self.click_func)

    def highlight(self) -> None:
        self.classes(remove='bg-blue-grey-2', add='bg-blue-grey-3')

    def unhighlight(self) -> None:
        self.classes(remove='bg-blue-grey-3', add='bg-blue-grey-2')

    def move_card(self) -> None:
        global dragged  # pylint: disable=global-statement # noqa: PLW0603
        self.unhighlight()
        dragged.parent_slot.parent.remove(dragged)
        with self:
            card(dragged.item)
        self.on_drop(dragged.item, self.name)
        dragged = None


class card(ui.card):

    def __init__(self, item: Item) -> None:
        super().__init__()
        self.item = item
        with self.props('draggable').classes('w-full cursor-pointer bg-grey-1'):
            ui.label(item.title)
        self.on('dragstart', self.handle_dragstart)
        self.on('click', self.on_click)

    def handle_dragstart(self) -> None:
        global dragged  # pylint: disable=global-statement # noqa: PLW0603
        dragged = self

    def on_click(self):
        print('click')
        with ui.dialog() as dialog, ui.card():
            ui.label(self.item.title)
            ui.input('Title', value=self.item.title)
            ui.button('Close', on_click=dialog.close)
        dialog.open()


@dataclass
class ToDo:
    title: str
    record: str


def handle_drop(todo: ToDo, location: str):
    todo.record.field.status = location
    update_records(todo.record)
    ui.notify(f'"{todo.title}" is now in {location}')


def click_func(todo: ToDo):
    ui.dialog(value=todo.title)


records = load_records()
need_info = [rec for rec in records if rec.field.status == 'Investigating/Additional information needed']
approved = [rec for rec in records if rec.field.status == 'Approved']
developing = [rec for rec in records if rec.field.status == 'Developing']
ready_for_development = [rec for rec in records if rec.field.status == 'Ready for Development']
with ui.row():
    with column('Need Info', on_drop=handle_drop):
        for rec in need_info:
            card(ToDo(rec.field.name, rec))

    with column('Developing', on_drop=handle_drop):
        for rec in developing:
            card(ToDo(rec.field.name, rec))

    with column('ready for dev', on_drop=handle_drop):
        for rec in ready_for_development:
            card(ToDo(rec.field.name, rec))

    with column('Approved', on_drop=handle_drop):
        for rec in records:
            card(ToDo(rec.field.name, rec))
ui.run()
