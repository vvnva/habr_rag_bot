from langsmith import Client

client = Client()

examples = [
    ("Что windows", "Windows 10 — операционная система для персональных компьютеров и рабочих станций, разработанная корпорацией Microsoft"),
    ("maven vs gradle, что выбрать?", "Maven больше подходит для небольших проектов, не требующих настройки процесса сборки, да и для которых время сборки проекта не так критично. Gradle больше подходит для масштабных проектов с большим количеством модулей, а также для Android-приложений."),
]

dataset_name = "tmp_dataset"
dataset = client.create_dataset(dataset_name=dataset_name)
inputs, outputs = zip(
    *[({"question": text}, {"ground_truth": label}) for text, label in examples]
)
client.create_examples(inputs=inputs, outputs=outputs, dataset_id=dataset.id)