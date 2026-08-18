# ML-задание: вероятность дефолта

Бинарная классификация по полю `Marker` (`good=1`, `bad=0`).
Основная метрика — **ROC-AUC**. API дополнительно возвращает
`probability_default = 1 - P(good)`.

Продакшен-код не дублирует препроцессинг: обучение, оценка и FastAPI
используют один sklearn `Pipeline` (импутация, `OrdinalEncoder` с
`handle_unknown`, XGBoost). Энкодер учится только на train-части.

## Структура

- `src/` — схема признаков, загрузка данных, пайплайн, I/O модели
- `train.py` — обучение и сохранение артефактов
- `evaluate.py` — оценка на `artifacts/data_test_*.csv` / `y_test_*.csv`
- `app.py` — FastAPI, `POST /predict`
- `ml.ipynb` — EDA и эксперименты (не требуется для инференса)
- `artifacts/` — данные, `model.joblib`, `metrics.json`, `training_config.json`
- `tests/` — pytest

## Требования

Python 3.10+. Для API и обучения:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Для тестов и ноутбука (pytest, shap, matplotlib):

```bash
pip install -r requirements-dev.txt
```

## Обучение

```bash
python train.py
```

Полезные флаги: `--quick` (узкая сетка гиперпараметров), `--cv`, `--test-size`.

Скрипт:

1. Стратифицированно делит выборку (`random_state=42`).
2. Подбирает гиперпараметры `GridSearchCV` по `roc_auc`.
3. Учитывает дисбаланс через `scale_pos_weight`.
4. Пишет:
   - `artifacts/model.joblib` — весь pipeline
   - `artifacts/metrics.json` — holdout ROC-AUC, PR-AUC, accuracy, best params
   - `artifacts/training_config.json` — seed, сетка, путь к данным

Неизвестные категории на инференсе кодируются как `-1`, пропуски импутируются
(`missing` / медиана). Строки с NA больше не выбрасываются целиком.

## Оценка на отложенных файлах

```bash
python evaluate.py
```

Результат: `artifacts/holdout_metrics.json`.

## API

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

- `GET /` и `GET /health` — статус и флаг загрузки модели
- `POST /predict` — multipart CSV

CSV должен быть UTF-8, с колонкой `ID` и всеми признаками из `src/features.py`.
Ответ — по одной записи на строку:

```json
{
  "n_rows": 2,
  "predictions": [
    {
      "id": "1",
      "prediction": 1,
      "probability_good": 0.91,
      "probability_default": 0.09
    }
  ]
}
```

Пример:

```bash
curl -s -F "file=@artifacts/data_test_1.csv" http://127.0.0.1:8000/predict
```

Ошибки: не-CSV / пустой файл / битая кодировка / нет колонок → 400;
нет артефакта модели → 503.

Документация OpenAPI: http://127.0.0.1:8000/docs

## Тесты

```bash
pytest
```

Покрывают схему признаков, unknown-категории, batch-predict, валидацию API
и smoke-обучение на крошечном датасете.

## Docker

Сначала должен существовать `artifacts/model.joblib` (`python train.py`).

```bash
cd docker
chmod +x docker-build.sh docker-compose-up.sh
./docker-build.sh
./docker-compose-up.sh
```

Образ: `bgpb-ml:latest`, порт `8000`. Healthcheck бьёт в `/health` через Python
(в slim-образе нет `curl`).

Либо:

```bash
docker build -t bgpb-ml:latest .
docker run --rm -p 8000:8000 bgpb-ml:latest
```

## Качество модели

Актуальные цифры после `python train.py` лежат в `artifacts/metrics.json`
и `artifacts/holdout_metrics.json`. На текущем прогоне:

| выборка | ROC-AUC | average precision | accuracy | n |
|---|---:|---:|---:|---:|
| holdout 20% от `data.csv` | 0.81 | 0.97 | 0.80 | 513 |
| `data_test_1.csv` | 0.96 | 0.99 | 0.88 | 26 |
| `data_test_2.csv` | 0.91 | 0.99 | 0.84 | 129 |

Классы несбалансированы (~11:1 good/bad), поэтому accuracy не является
целевой метрикой: GridSearchCV оптимизирует ROC-AUC.

Ноутбук `ml.ipynb` — исследование; воспроизводимый пайплайн для сдачи — `train.py`.

## Ограничения

- Целевой класс в данных: `1 = good`. Вероятность дефолта — дополнительное поле ответа.
- Holdout `data_test_*` не участвует в подборе гиперпараметров.
- Docker-образ API не содержит обучающий `data.csv`.
- На macOS для локального XGBoost нужен OpenMP: `brew install libomp`.
  Альтернатива — прогон тестов и обучения в Linux-контейнере:
  `docker build -f Dockerfile.train -t bgpb-ml-train . && docker run --rm bgpb-ml-train`.
