# Diagrama ER — Sistema de E-commerce

Exemplo com dados fictícios para demonstrar as capacidades do Mermaid ER diagrams.

## Diagrama Completo

```mermaid
erDiagram
    CUSTOMER {
        int     id          PK
        string  name
        string  email
        string  phone
        date    created_at
    }

    ADDRESS {
        int     id          PK
        int     customer_id FK
        string  street
        string  city
        string  postal_code
        string  country
        boolean is_default
    }

    ORDER {
        int     id          PK
        int     customer_id FK
        int     address_id  FK
        string  status
        decimal total_amount
        date    ordered_at
    }

    ORDER_ITEM {
        int     id          PK
        int     order_id    FK
        int     product_id  FK
        int     quantity
        decimal unit_price
    }

    PRODUCT {
        int     id          PK
        int     category_id FK
        int     supplier_id FK
        string  name
        string  description
        decimal price
        int     stock
    }

    CATEGORY {
        int     id     PK
        string  name
        int     parent_id FK
    }

    SUPPLIER {
        int     id      PK
        string  name
        string  email
        string  country
    }

    PAYMENT {
        int     id         PK
        int     order_id   FK
        string  method
        string  status
        decimal amount
        date    paid_at
    }

    REVIEW {
        int     id          PK
        int     customer_id FK
        int     product_id  FK
        int     rating
        string  comment
        date    created_at
    }

    %% Relações
    CUSTOMER    ||--o{  ADDRESS     : "tem"
    CUSTOMER    ||--o{  ORDER       : "faz"
    CUSTOMER    ||--o{  REVIEW      : "escreve"

    ORDER       ||--|{  ORDER_ITEM  : "contém"
    ORDER       }o--||  ADDRESS     : "entregue em"
    ORDER       ||--o|  PAYMENT     : "pago por"

    ORDER_ITEM  }o--||  PRODUCT     : "refere"

    PRODUCT     }o--||  CATEGORY    : "pertence a"
    PRODUCT     }o--||  SUPPLIER    : "fornecido por"
    PRODUCT     ||--o{  REVIEW      : "recebe"

    CATEGORY    }o--o|  CATEGORY    : "sub-categoria de"
```

---

## Legenda de Cardinalidades

| Símbolo | Significado              |
|---------|--------------------------|
| `\|\|`  | Exatamente um            |
| `o\|`   | Zero ou um               |
| `\|\{`  | Um ou mais               |
| `o{`    | Zero ou mais             |

---

## Dados de Exemplo

### Clientes
| id | name           | email                  | phone       |
|----|----------------|------------------------|-------------|
| 1  | Ana Silva      | ana@email.com          | 912 345 678 |
| 2  | Bruno Costa    | bruno@email.com        | 961 234 567 |
| 3  | Catarina Neves | catarina@email.com     | 935 678 901 |

### Produtos
| id | name              | category_id | price   | stock |
|----|-------------------|-------------|---------|-------|
| 1  | Laptop Pro 15"    | 1           | 1299.99 | 15    |
| 2  | Teclado Mecânico  | 2           | 89.90   | 42    |
| 3  | Monitor 27" 4K    | 1           | 449.00  | 8     |

### Encomendas
| id | customer_id | status    | total_amount | ordered_at |
|----|-------------|-----------|--------------|------------|
| 1  | 1           | entregue  | 1389.89      | 2026-01-10 |
| 2  | 2           | expedido  | 449.00       | 2026-02-01 |
| 3  | 3           | pendente  | 89.90        | 2026-02-19 |

---

## Notas sobre a Sintaxe Mermaid ER

- **`PK`** — Primary Key (chave primária)
- **`FK`** — Foreign Key (chave estrangeira)
- Tipos suportados: `string`, `int`, `decimal`, `boolean`, `date`, etc.
- Relações auto-referenciadas são suportadas (ex: `CATEGORY` → `CATEGORY`)
