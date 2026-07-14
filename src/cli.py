"""CLI интерфейс для Password Manager"""
import click
import sys
import os
from getpass import getpass
from src.password_manager import PasswordManager
from src.password_generator import PasswordGenerator
from src.password_strength import PasswordStrengthAnalyzer


@click.group()
def cli():
    """Password Manager - безопасное хранение паролей"""
    pass


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
def init(vault):
    """Инициализация нового хранилища"""
    master_password = getpass("Введите мастер-пароль: ")
    confirm = getpass("Подтвердите мастер-пароль: ")
    
    if master_password != confirm:
        click.echo("❌ Пароли не совпадают", err=True)
        sys.exit(1)
    
    if len(master_password) < 8:
        click.echo("❌ Мастер-пароль должен быть минимум 8 символов", err=True)
        sys.exit(1)
    
    manager = PasswordManager(master_password, vault)
    manager._save_vault()
    click.echo(f"✅ Хранилище создано: {manager.storage.vault_path}")


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
def list(vault):
    """Список всех записей"""
    master_password = getpass("Введите мастер-пароль: ")
    
    try:
        manager = PasswordManager(master_password, vault)
        entries = manager.list_entries()
        
        if not entries:
            click.echo("📭 Хранилище пусто")
            return
        
        click.echo(f"\n📋 Всего записей: {len(entries)}")
        for i, entry in enumerate(entries, 1):
            click.echo(f"\n{i}. 🔐 {entry.login}")
            click.echo(f"   ID: {entry.id[:8]}...")
            click.echo(f"   Пароль: {entry.password}")
            click.echo(f"   URL: {entry.url or 'Нет'}")
            click.echo(f"   Заметка: {entry.note or 'Нет'}")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
@click.option('--login', prompt='Логин', help='Логин')
@click.option('--password', prompt=False, help='Пароль')
@click.option('--url', default='', help='URL')
@click.option('--note', default='', help='Заметка')
@click.option('--generate', is_flag=True, help='Сгенерировать пароль')
def add(vault, login, password, url, note, generate):
    """Добавление новой записи"""
    if generate or not password:
        gen = PasswordGenerator()
        password = gen.generate(length=16)
        click.echo(f"🔑 Сгенерирован пароль: {password}")
    elif not password:
        password = getpass("Введите пароль: ")
    
    master_password = getpass("Введите мастер-пароль: ")
    
    try:
        manager = PasswordManager(master_password, vault)
        entry = manager.add_entry(login, password, url, note)
        click.echo(f"✅ Запись добавлена. ID: {entry.id[:8]}...")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
@click.argument('query')
def search(vault, query):
    """Поиск записей"""
    master_password = getpass("Введите мастер-пароль: ")
    
    try:
        manager = PasswordManager(master_password, vault)
        results = manager.search_entries(query)
        
        if not results:
            click.echo(f"🔍 По запросу '{query}' ничего не найдено")
            return
        
        click.echo(f"\n🔍 Найдено записей: {len(results)}")
        for entry in results:
            click.echo(f"\n🔐 {entry.login}")
            click.echo(f"   ID: {entry.id[:8]}...")
            click.echo(f"   Пароль: {entry.password}")
            click.echo(f"   URL: {entry.url or 'Нет'}")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
@click.argument('entry_id')
def delete(vault, entry_id):
    """Удаление записи по ID"""
    master_password = getpass("Введите мастер-пароль: ")
    
    try:
        manager = PasswordManager(master_password, vault)
        entry = manager.get_entry(entry_id)
        
        if not entry:
            click.echo(f"❌ Запись с ID {entry_id} не найдена", err=True)
            sys.exit(1)
        
        click.echo(f"\n🔐 {entry.login}")
        click.confirm("Удалить эту запись?", abort=True)
        
        if manager.delete_entry(entry_id):
            click.echo("✅ Запись удалена")
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--vault', default='data/vault.vault', help='Путь к хранилищу')
@click.option('--output', default='data/export.vault', help='Путь для экспорта')
def export(vault, output):
    """Экспорт хранилища"""
    master_password = getpass("Введите мастер-пароль: ")
    
    try:
        manager = PasswordManager(master_password, vault)
        manager.export_vault(output)
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--length', default=16, help='Длина пароля')
def generate(length):
    """Генерация пароля"""
    gen = PasswordGenerator()
    password = gen.generate(length=length)
    click.echo(f"\n🔑 Пароль: {password}")

@cli.command()
@click.argument('password')
def check(password):
    """Проверка стойкости пароля"""
    analyzer = PasswordStrengthAnalyzer()
    result = analyzer.classify_strength(password)
    click.echo(f"\n📊 Результаты:")
    click.echo(f"   Длина: {result['length']} символов")
    click.echo(f"   Энтропия: {result['entropy']} бит")
    click.echo(f"   Стойкость: {result['strength']}")
    if result['warnings']:
        click.echo(f"\n⚠️ Предупреждения:")
        for warning in result['warnings']:
            click.echo(f"   - {warning}")

if __name__ == '__main__':
    cli()