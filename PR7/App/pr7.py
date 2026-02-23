import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, colorchooser
import math

class NetworkNode:
    def __init__(self, node_id, x, y, name=None):
        self.id = node_id
        self.x = x
        self.y = y
        self.name = name if name else f"Узел {node_id}"
        self.type = "Компьютер"
        self.selected = False
        self.radius = 15

class NetworkEdge:
    def __init__(self, edge_id, node1, node2, bandwidth=100):
        self.id = edge_id
        self.node1 = node1
        self.node2 = node2
        self.bandwidth = bandwidth
        self.selected = False
        self.color = "black"

class NetworkTopologyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Топология компьютерной сети")
        self.root.geometry("1000x700")
        
        self.nodes = []
        self.edges = []
        self.next_node_id = 1
        self.next_edge_id = 1
        self.selected_node = None
        self.selected_edge = None
        self.temp_edge_start = None
        self.drag_data = {"x": 0, "y": 0, "item": None}
        
        self.setup_menu()
        self.setup_ui()
        self.setup_bindings()
        
        self.root.mainloop()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Очистить все", command=self.clear_all)
        file_menu.add_command(label="Пример сети", command=self.create_example_network)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        edit_menu.add_command(label="Добавить узел", command=self.add_node_dialog)
        edit_menu.add_command(label="Добавить соединение", command=self.start_add_edge)
        edit_menu.add_separator()
        edit_menu.add_command(label="Удалить выбранное", command=self.delete_selected)
        edit_menu.add_command(label="Свойства", command=self.edit_properties)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        control_frame = ttk.Frame(main_frame, relief=tk.RAISED, borderwidth=1)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(control_frame, text="Добавить узел", 
                  command=self.add_node_dialog).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Добавить соединение", 
                  command=self.start_add_edge).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Удалить выбранное", 
                  command=self.delete_selected).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Свойства", 
                  command=self.edit_properties).pack(side=tk.LEFT, padx=5, pady=5)
        
        self.status_label = ttk.Label(control_frame, text="Готов к работе")
        self.status_label.pack(side=tk.RIGHT, padx=10)
        
        self.canvas = tk.Canvas(main_frame, bg='white', highlightthickness=1, 
                               highlightbackground='gray')
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def setup_bindings(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
    
    def add_node_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить узел")
        dialog.geometry("300x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название узла:", font=('Arial', 10)).pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, f"Узел {self.next_node_id}")
        
        ttk.Label(dialog, text="Тип устройства:", font=('Arial', 10)).pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=["Компьютер", "Сервер", "Маршрутизатор", "Коммутатор", "Брандмауэр"])
        type_combo.pack(pady=5)
        type_combo.set("Компьютер")
        
        def add_node():
            x = 150 + (len(self.nodes) * 50) % 700
            y = 150 + (len(self.nodes) * 30) % 400
            node = NetworkNode(self.next_node_id, x, y, name_entry.get())
            node.type = type_combo.get()
            self.nodes.append(node)
            self.next_node_id += 1
            self.draw_node(node)
            dialog.destroy()
            self.update_status(f"Добавлен узел: {node.name} ({node.type})")
        
        ttk.Button(dialog, text="Добавить", command=add_node, width=15).pack(pady=15)
    
    def start_add_edge(self):
        if len(self.nodes) < 2:
            messagebox.showwarning("Предупреждение", "Нужно хотя бы 2 узла для создания соединения")
            return
        self.temp_edge_start = None
        self.update_status("Режим добавления соединения: выберите первый узел")
    
    def draw_node(self, node):
        color = self.get_node_color(node.type)
        outline = 'blue' if node.selected else 'black'
        width = 3 if node.selected else 2
        
        x1, y1 = node.x - node.radius, node.y - node.radius
        x2, y2 = node.x + node.radius, node.y + node.radius
        
        node.oval = self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline=outline, width=width)
        node.text = self.canvas.create_text(node.x, node.y + 25, text=node.name, font=('Arial', 9))
        
        if node.type != "Компьютер":
            type_text = self.canvas.create_text(node.x, node.y - 25, text=node.type, 
                                               font=('Arial', 8), fill='gray')
            node.type_text = type_text
    
    def get_node_color(self, node_type):
        colors = {
            "Компьютер": "#ADD8E6",
            "Сервер": "#FFB6C1",
            "Маршрутизатор": "#90EE90",
            "Коммутатор": "#FFD700",
            "Брандмауэр": "#FFA07A"
        }
        return colors.get(node_type, "#D3D3D3")
    
    def draw_edge(self, edge):
        x1, y1 = edge.node1.x, edge.node1.y
        x2, y2 = edge.node2.x, edge.node2.y
        
        color = 'red' if edge.selected else 'gray'
        width = 3 if edge.selected else 2
        
        edge.line = self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
        
        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
        edge.text = self.canvas.create_text(mx, my - 10, text=f"{edge.bandwidth} Mbps", 
                                           font=('Arial', 8), fill='blue')
    
    def redraw_all(self):
        self.canvas.delete("all")
        for edge in self.edges:
            self.draw_edge(edge)
        for node in self.nodes:
            self.draw_node(node)
    
    def on_click(self, event):
        x, y = event.x, event.y
        
        for node in reversed(self.nodes):
            if (node.x - node.radius <= x <= node.x + node.radius and 
                node.y - node.radius <= y <= node.y + node.radius):
                
                if self.temp_edge_start is None:
                    self.select_node(node)
                    self.drag_data["item"] = node
                    self.drag_data["x"] = x
                    self.drag_data["y"] = y
                else:
                    if node != self.temp_edge_start:
                        bandwidth = simpledialog.askinteger("Пропускная способность", 
                                                           "Введите пропускную способность (Mbps):",
                                                           initialvalue=100, minvalue=1, maxvalue=10000)
                        if bandwidth:
                            edge = NetworkEdge(self.next_edge_id, self.temp_edge_start, node, bandwidth)
                            self.edges.append(edge)
                            self.next_edge_id += 1
                            self.draw_edge(edge)
                            self.update_status(f"Добавлено соединение: {bandwidth} Mbps")
                    self.temp_edge_start = None
                    self.clear_selection()
                return
        
        for edge in self.edges:
            if self.point_near_line(x, y, edge.node1.x, edge.node1.y, edge.node2.x, edge.node2.y):
                self.select_edge(edge)
                return
        
        self.clear_selection()
        self.temp_edge_start = None
        self.update_status("Готов к работе")
    
    def on_drag(self, event):
        if self.drag_data["item"]:
            node = self.drag_data["item"]
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            
            node.x = max(node.radius, min(1000 - node.radius, node.x + dx))
            node.y = max(node.radius, min(700 - node.radius, node.y + dy))
            
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            
            self.redraw_all()
    
    def on_release(self, event):
        self.drag_data["item"] = None
    
    def on_right_click(self, event):
        x, y = event.x, event.y
        
        for node in self.nodes:
            if (node.x - node.radius <= x <= node.x + node.radius and 
                node.y - node.radius <= y <= node.y + node.radius):
                self.show_node_menu(event, node)
                return
        
        for edge in self.edges:
            if self.point_near_line(x, y, edge.node1.x, edge.node1.y, edge.node2.x, edge.node2.y):
                self.show_edge_menu(event, edge)
                return
    
    def point_near_line(self, px, py, x1, y1, x2, y2, tolerance=5):
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1) <= tolerance
        
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        if t < 0:
            t = 0
        elif t > 1:
            t = 1
        
        proj_x = x1 + t * dx
        proj_y = y1 + t * dy
        
        distance = math.hypot(px - proj_x, py - proj_y)
        return distance <= tolerance
    
    def select_node(self, node):
        self.clear_selection()
        node.selected = True
        self.selected_node = node
        self.redraw_all()
        self.update_status(f"Выбран узел: {node.name} ({node.type})")
    
    def select_edge(self, edge):
        self.clear_selection()
        edge.selected = True
        self.selected_edge = edge
        self.redraw_all()
        self.update_status(f"Выбрано соединение: {edge.bandwidth} Mbps")
    
    def clear_selection(self):
        for node in self.nodes:
            node.selected = False
        for edge in self.edges:
            edge.selected = False
        self.selected_node = None
        self.selected_edge = None
        self.redraw_all()
    
    def delete_selected(self):
        if self.selected_node:
            if messagebox.askyesno("Подтверждение", f"Удалить узел '{self.selected_node.name}' и все его соединения?"):
                edges_to_remove = [e for e in self.edges if e.node1 == self.selected_node or e.node2 == self.selected_node]
                for edge in edges_to_remove:
                    self.edges.remove(edge)
                self.nodes.remove(self.selected_node)
                self.clear_selection()
                self.redraw_all()
                self.update_status("Узел и связанные соединения удалены")
        elif self.selected_edge:
            if messagebox.askyesno("Подтверждение", "Удалить выбранное соединение?"):
                self.edges.remove(self.selected_edge)
                self.clear_selection()
                self.redraw_all()
                self.update_status("Соединение удалено")
        else:
            messagebox.showinfo("Информация", "Ничего не выбрано для удаления")
    
    def edit_properties(self):
        if self.selected_node:
            self.edit_node_properties(self.selected_node)
        elif self.selected_edge:
            self.edit_edge_properties(self.selected_edge)
        else:
            messagebox.showinfo("Информация", "Выберите узел или соединение для редактирования")
    
    def edit_node_properties(self, node):
        dialog = tk.Toplevel(self.root)
        dialog.title("Свойства узла")
        dialog.geometry("300x250")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название:", font=('Arial', 10)).pack(pady=5)
        name_entry = ttk.Entry(dialog, width=30)
        name_entry.pack(pady=5)
        name_entry.insert(0, node.name)
        
        ttk.Label(dialog, text="Тип:", font=('Arial', 10)).pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=["Компьютер", "Сервер", "Маршрутизатор", "Коммутатор", "Брандмауэр"])
        type_combo.pack(pady=5)
        type_combo.set(node.type)
        
        def save():
            node.name = name_entry.get()
            node.type = type_combo.get()
            self.redraw_all()
            dialog.destroy()
            self.update_status("Свойства узла обновлены")
        
        ttk.Button(dialog, text="Сохранить", command=save, width=15).pack(pady=15)
    
    def edit_edge_properties(self, edge):
        bandwidth = simpledialog.askinteger("Пропускная способность", 
                                           "Введите новую пропускную способность (Mbps):",
                                           initialvalue=edge.bandwidth, minvalue=1, maxvalue=10000)
        if bandwidth:
            edge.bandwidth = bandwidth
            self.redraw_all()
            self.update_status(f"Пропускная способность обновлена: {bandwidth} Mbps")
    
    def show_node_menu(self, event, node):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Редактировать", command=lambda: self.edit_node_properties(node))
        menu.add_command(label="Удалить", command=lambda: self.delete_node(node))
        menu.add_separator()
        menu.add_command(label="Начать соединение отсюда", command=lambda: self.start_edge_from_node(node))
        menu.post(event.x_root, event.y_root)
    
    def show_edge_menu(self, event, edge):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Редактировать", command=lambda: self.edit_edge_properties(edge))
        menu.add_command(label="Удалить", command=lambda: self.delete_edge(edge))
        menu.post(event.x_root, event.y_root)
    
    def delete_node(self, node):
        if messagebox.askyesno("Подтверждение", f"Удалить узел '{node.name}'?"):
            edges_to_remove = [e for e in self.edges if e.node1 == node or e.node2 == node]
            for edge in edges_to_remove:
                self.edges.remove(edge)
            self.nodes.remove(node)
            self.clear_selection()
            self.redraw_all()
            self.update_status("Узел удален")
    
    def delete_edge(self, edge):
        if messagebox.askyesno("Подтверждение", "Удалить соединение?"):
            self.edges.remove(edge)
            self.clear_selection()
            self.redraw_all()
            self.update_status("Соединение удалено")
    
    def start_edge_from_node(self, node):
        self.temp_edge_start = node
        self.update_status(f"Режим добавления соединения: выберите второй узел для связи с {node.name}")
        self.clear_selection()
    
    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Очистить всю сеть?"):
            self.nodes.clear()
            self.edges.clear()
            self.next_node_id = 1
            self.next_edge_id = 1
            self.selected_node = None
            self.selected_edge = None
            self.temp_edge_start = None
            self.canvas.delete("all")
            self.update_status("Сеть очищена")
    
    def create_example_network(self):
        self.clear_all()
        
        nodes_data = [
            ("Сервер 1", "Сервер", 200, 150),
            ("Сервер 2", "Сервер", 200, 350),
            ("Маршрутизатор", "Маршрутизатор", 400, 250),
            ("Коммутатор", "Коммутатор", 600, 150),
            ("Брандмауэр", "Брандмауэр", 600, 350),
            ("ПК 1", "Компьютер", 800, 100),
            ("ПК 2", "Компьютер", 800, 200),
            ("ПК 3", "Компьютер", 800, 300),
            ("ПК 4", "Компьютер", 800, 400)
        ]
        
        for name, type_name, x, y in nodes_data:
            node = NetworkNode(self.next_node_id, x, y, name)
            node.type = type_name
            self.nodes.append(node)
            self.next_node_id += 1
        
        edges_data = [
            (0, 2, 1000),
            (1, 2, 1000),
            (2, 3, 1000),
            (2, 4, 1000),
            (3, 5, 100),
            (3, 6, 100),
            (4, 7, 100),
            (4, 8, 100)
        ]
        
        for n1, n2, bw in edges_data:
            if n1 < len(self.nodes) and n2 < len(self.nodes):
                edge = NetworkEdge(self.next_edge_id, self.nodes[n1], self.nodes[n2], bw)
                self.edges.append(edge)
                self.next_edge_id += 1
        
        self.redraw_all()
        self.update_status("Создана примерная сеть")
    
    def update_status(self, message):
        self.status_label.config(text=message)

if __name__ == "__main__":
    app = NetworkTopologyApp()