import json
import pickle
from sklearn.neighbors import NearestNeighbors
import logging

logger = logging.getLogger(__name__)

def get_category_groups():
    """Agrupa categorias similares"""
    try:
        category_groups = {
            # Grupo 0: Suspense/Mistério
            "Thriller": 0,
            "Mystery": 0,
            
            # Grupo 1: Viagem/Gastronomia
            "Travel": 1,
            "Food and Drink": 1,
            
            # Grupo 2: Ficção
            "Fiction": 2,
            "Historical Fiction": 2,
            "Science Fiction": 2,
            
            # Grupo 3: Literatura
            "Poetry": 3,
            
            # Grupo 4: Infantil/Jovem
            "Childrens": 4,
            "Young Adult": 4,
            
            # Grupo 5: Romance
            "Romance": 5,
            
            # Grupo 6: Não-ficção
            "Nonfiction": 6,
            "History": 6,
            "Philosophy": 6,
            "Spirituality": 6,
            
            # Grupo 7: Arte/Música
            "Art": 7,
            "Music": 7,
            "Sequential Art": 7,
            
            # Grupo 8: Negócios/Política
            "Business": 8,
            "Politics": 8,
            
            # Grupo 9: Outros
            "Default": 9
        }
        return category_groups
    except Exception as e:
        logger.error(f"Erro ao criar mapa de grupos de categorias: {e}")
        return {}

def train_recommendation_model():
    """Treina o modelo de recomendação e salva em model.pkl"""
    print("Treinando modelo...")
    
    # Carregar dados com tratamento de erro
    try:
        with open("books.json") as f:
            BOOK_LIST = json.load(f)
        print(f"Total de livros carregados: {len(BOOK_LIST)}")
    except FileNotFoundError:
        print("Erro: Arquivo books.json não encontrado")
        return
    except json.JSONDecodeError:
        print("Erro: Arquivo books.json está corrompido")
        return
    except Exception as e:
        print(f"Erro ao carregar books.json: {e}")
        return
    
    # Verificar se há livros
    if not BOOK_LIST:
        print("Erro: Nenhum livro encontrado no arquivo")
        return
    
    # Usa grupos ao invés de categorias individuais
    category_groups = get_category_groups()
    
    if not category_groups:
        print("Erro: Não foi possível criar mapa de categorias")
        return
    
    # Preparar dados de treino
    X = []
    for book in BOOK_LIST:
        book_category = book.get("category")
        
        # Verificar se a categoria existe no mapa
        if book_category not in category_groups:
            print(f"Aviso: Categoria '{book_category}' não encontrada no mapa. Pulando livro.")
            continue
        
        group_number = category_groups[book_category]
        X.append([group_number])
    
    # Verificar se há dados suficientes
    if len(X) < 6:
        print(f"Erro: Dados insuficientes para treinar. Apenas {len(X)} livros válidos.")
        return
    
    print(f"Total de livros válidos para treino: {len(X)}")
    
    # Treinar modelo
    try:
        model = NearestNeighbors(n_neighbors=6)
        model.fit(X)
        print("Modelo treinado com sucesso!")
    except Exception as e:
        print(f"Erro ao treinar modelo: {e}")
        return
    
    # Salvar modelo
    try:
        with open("model.pkl", "wb") as f:
            pickle.dump(model, f)
        print("Modelo salvo em 'model.pkl'")
    except Exception as e:
        print(f"Erro ao salvar modelo: {e}")
        return
    
    print(f"Total de grupos: {len(set(category_groups.values()))}")
    print("Processo concluído com sucesso!")

if __name__ == "__main__":
    train_recommendation_model()
