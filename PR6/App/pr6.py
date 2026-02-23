import tkinter as tk
from tkinter import ttk, messagebox

class DecisionTreeNode:
    def __init__(self, question=None, result=None):
        self.question = question
        self.result = result
        self.yes_branch = None
        self.no_branch = None
        self.parent = None

class DecisionTreeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Дерево решений")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        self.current_node = None
        self.history = []
        self.tree_nodes = {}
        
        self.build_decision_tree()
        self.setup_ui()
        self.display_tree()
        self.reset_to_root()
        
        self.root.mainloop()
    
    def build_decision_tree(self):
        root = DecisionTreeNode(question="Запускать новый продукт?")
        
        node1 = DecisionTreeNode(question="Высокий спрос?")
        node1.parent = root
        root.yes_branch = node1
        
        node2 = DecisionTreeNode(question="Высокая прибыль?")
        node2.parent = node1
        node1.yes_branch = node2
        
        node3 = DecisionTreeNode(question="Низкая конкуренция?")
        node3.parent = node2
        node2.yes_branch = node3
        
        node3.yes_branch = DecisionTreeNode(result="Запускать немедленно")
        node3.yes_branch.parent = node3
        node3.no_branch = DecisionTreeNode(result="Нужно УТП")
        node3.no_branch.parent = node3
        
        node4 = DecisionTreeNode(question="Высокая конкуренция?")
        node4.parent = node2
        node2.no_branch = node4
        
        node4.yes_branch = DecisionTreeNode(result="Анализировать конкурентов")
        node4.yes_branch.parent = node4
        node4.no_branch = DecisionTreeNode(result="Искать нишу")
        node4.no_branch.parent = node4
        
        node5 = DecisionTreeNode(question="Низкая себестоимость?")
        node5.parent = node1
        node1.no_branch = node5
        
        node5.yes_branch = DecisionTreeNode(result="Запускать с осторожностью")
        node5.yes_branch.parent = node5
        node5.no_branch = DecisionTreeNode(result="Оптимизировать производство")
        node5.no_branch.parent = node5
        
        node6 = DecisionTreeNode(question="Есть сезонность?")
        node6.parent = root
        root.no_branch = node6
        
        node7 = DecisionTreeNode(question="Пик спроса скоро?")
        node7.parent = node6
        node6.yes_branch = node7
        
        node7.yes_branch = DecisionTreeNode(result="Готовиться к запуску")
        node7.yes_branch.parent = node7
        node7.no_branch = DecisionTreeNode(result="Отложить запуск")
        node7.no_branch.parent = node7
        
        node8 = DecisionTreeNode(question="Пик спроса не скоро?")
        node8.parent = node6
        node6.no_branch = node8
        
        node8.yes_branch = DecisionTreeNode(result="Развивать в низкий сезон")
        node8.yes_branch.parent = node8
        node8.no_branch = DecisionTreeNode(result="Искать другой рынок")
        node8.no_branch.parent = node8
        
        self.root_node = root
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="Дерево решений", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=5)
        
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(paned_window, relief=tk.SUNKEN, borderwidth=1)
        paned_window.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Структура дерева решений", 
                 font=('Arial', 10, 'bold')).pack(pady=5)
        
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree_canvas = tk.Canvas(tree_frame, bg='white')
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_canvas.yview)
        self.tree_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.tree_frame_inner = ttk.Frame(self.tree_canvas)
        self.tree_canvas.create_window((0, 0), window=self.tree_frame_inner, anchor='nw')
        
        self.tree_frame_inner.bind('<Configure>', self.on_frame_configure)
        self.tree_canvas.bind_all('<MouseWheel>', self.on_mousewheel)
        
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=1)
        
        question_frame = ttk.LabelFrame(right_frame, text="Текущий вопрос", padding="10")
        question_frame.pack(fill=tk.X, pady=5)
        
        self.question_label = ttk.Label(question_frame, text="", 
                                       font=('Arial', 12, 'bold'), wraplength=350)
        self.question_label.pack(pady=10)
        
        button_frame = ttk.Frame(question_frame)
        button_frame.pack(pady=10)
        
        self.yes_button = ttk.Button(button_frame, text="Да", command=self.answer_yes, 
                                     width=15, state=tk.DISABLED)
        self.yes_button.pack(side=tk.LEFT, padx=5)
        
        self.no_button = ttk.Button(button_frame, text="Нет", command=self.answer_no, 
                                    width=15, state=tk.DISABLED)
        self.no_button.pack(side=tk.LEFT, padx=5)
        
        result_frame = ttk.LabelFrame(right_frame, text="Результат", padding="10")
        result_frame.pack(fill=tk.X, pady=5)
        
        self.result_label = ttk.Label(result_frame, text="", 
                                      font=('Arial', 11), wraplength=350)
        self.result_label.pack(pady=10)
        
        history_frame = ttk.LabelFrame(right_frame, text="История ответов", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.history_listbox = tk.Listbox(history_frame, height=8, font=('Arial', 9))
        self.history_listbox.pack(fill=tk.BOTH, expand=True)
        
        nav_frame = ttk.Frame(right_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        self.back_button = ttk.Button(nav_frame, text="Назад", command=self.go_back, 
                                      width=15, state=tk.DISABLED)
        self.back_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(nav_frame, text="Сброс", command=self.reset_to_root, 
                                       width=15)
        self.back_button.pack(side=tk.LEFT, padx=5)
        self.reset_button.pack(side=tk.LEFT, padx=5)
    
    def on_frame_configure(self, event):
        self.tree_canvas.configure(scrollregion=self.tree_canvas.bbox('all'))
    
    def on_mousewheel(self, event):
        self.tree_canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
    
    def display_tree(self):
        for widget in self.tree_frame_inner.winfo_children():
            widget.destroy()
        
        self.tree_nodes = {}
        self._display_node(self.root_node, 0, 0)
    
    def _display_node(self, node, level, index):
        if not node:
            return
        
        padding = 20
        x_pos = level * 30
        
        if node.question:
            text = f"{'  ' * level}• {node.question}"
        else:
            text = f"{'  ' * level}• РЕЗУЛЬТАТ: {node.result}"
        
        frame = ttk.Frame(self.tree_frame_inner)
        frame.pack(anchor=tk.W, pady=2)
        
        label = ttk.Label(frame, text=text, font=('Courier', 9), wraplength=300)
        label.pack(side=tk.LEFT)
        
        self.tree_nodes[node] = label
        
        if node == self.current_node:
            label.configure(foreground='blue', font=('Courier', 9, 'bold'))
        
        if node.yes_branch:
            self._display_node(node.yes_branch, level + 1, index * 2)
        if node.no_branch:
            self._display_node(node.no_branch, level + 1, index * 2 + 1)
    
    def reset_to_root(self):
        self.current_node = self.root_node
        self.history = []
        self.update_ui()
    
    def answer_yes(self):
        if self.current_node and self.current_node.yes_branch:
            self.history.append((self.current_node.question, "Да"))
            self.current_node = self.current_node.yes_branch
            self.update_ui()
    
    def answer_no(self):
        if self.current_node and self.current_node.no_branch:
            self.history.append((self.current_node.question, "Нет"))
            self.current_node = self.current_node.no_branch
            self.update_ui()
    
    def go_back(self):
        if self.history and self.current_node:
            if self.current_node.parent:
                self.current_node = self.current_node.parent
                self.history.pop()
                self.update_ui()
    
    def update_ui(self):
        self.display_tree()
        
        if self.current_node:
            if self.current_node.question:
                self.question_label.config(text=self.current_node.question)
                self.result_label.config(text="")
                self.yes_button.config(state=tk.NORMAL)
                self.no_button.config(state=tk.NORMAL)
                
                if not self.current_node.yes_branch:
                    self.yes_button.config(state=tk.DISABLED)
                if not self.current_node.no_branch:
                    self.no_button.config(state=tk.DISABLED)
            else:
                self.question_label.config(text="")
                self.result_label.config(text=self.current_node.result)
                self.yes_button.config(state=tk.DISABLED)
                self.no_button.config(state=tk.DISABLED)
        
        self.history_listbox.delete(0, tk.END)
        for i, (question, answer) in enumerate(self.history, 1):
            self.history_listbox.insert(tk.END, f"{i}. {question} -> {answer}")
        
        if len(self.history) > 0:
            self.back_button.config(state=tk.NORMAL)
        else:
            self.back_button.config(state=tk.DISABLED)
        
        self.history_listbox.yview_moveto(1)

if __name__ == "__main__":
    app = DecisionTreeApp()