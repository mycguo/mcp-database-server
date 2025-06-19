-- ToDo App Database Schema for PostgreSQL
-- Run this script to create the tables for your ToDo application

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#007bff', -- hex color code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, name)
);

-- Create todos table
CREATE TABLE todos (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    due_date TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Create indexes for better performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_categories_user_id ON categories(user_id);

-- Insert sample data
INSERT INTO users (username, email, password_hash) VALUES
('john_doe', 'john@example.com', '$2b$12$hash1'),
('jane_smith', 'jane@example.com', '$2b$12$hash2'),
('bob_wilson', 'bob@example.com', '$2b$12$hash3');

INSERT INTO categories (user_id, name, color) VALUES
(1, 'Work', '#dc3545'),
(1, 'Personal', '#28a745'),
(1, 'Shopping', '#ffc107'),
(2, 'Projects', '#17a2b8'),
(2, 'Health', '#6f42c1'),
(3, 'Home', '#fd7e14');

INSERT INTO todos (user_id, category_id, title, description, priority, status, due_date) VALUES
(1, 1, 'Complete project proposal', 'Finish the Q4 project proposal for client meeting', 'high', 'in_progress', '2024-01-15 17:00:00'),
(1, 1, 'Review team performance', 'Conduct quarterly review with team members', 'medium', 'pending', '2024-01-20 10:00:00'),
(1, 2, 'Buy groceries', 'Milk, bread, eggs, fruits', 'low', 'pending', '2024-01-12 18:00:00'),
(1, 3, 'Get car serviced', 'Annual maintenance check', 'medium', 'pending', '2024-01-18 09:00:00'),
(2, 4, 'Learn PostgreSQL', 'Complete online course on database management', 'high', 'in_progress', '2024-01-25 23:59:59'),
(2, 5, 'Doctor appointment', 'Annual health checkup', 'high', 'pending', '2024-01-14 14:30:00'),
(3, 6, 'Fix leaky faucet', 'Kitchen sink needs repair', 'medium', 'pending', '2024-01-16 12:00:00'),
(1, 2, 'Plan weekend trip', 'Research destinations and book accommodation', 'low', 'completed', '2024-01-10 15:00:00');

-- Update completed todos with completion time
UPDATE todos SET completed_at = '2024-01-10 16:30:00' WHERE status = 'completed'; 