import aiosqlite


async def db_start():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()

        await cur.execute("CREATE TABLE IF NOT EXISTS accounts ("
                          "user_id INTEGER PRIMARY KEY,"
                          "service TEXT, "
                          "name TEXT, "
                          "surname TEXT,"
                          "date_client TEXT, "
                          "phone INTEGER) ")

        await cur.execute("CREATE TABLE IF NOT EXISTS dates ("
                          "user_id INTEGER PRIMARY KEY,"
                          "date_admin TEXT) ")
        await cur.execute('''
                    CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        UNIQUE(user_id)
                    )
                ''')

        await db.commit()


async def get_all_clients():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT * FROM accounts")
        clients = await cur.fetchall()
        return clients


async def get_all_dates():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT * FROM dates")
        dates = await cur.fetchall()
        return dates


async def write_date(state):
    async with aiosqlite.connect('utils/tg.db') as db:
        async with state.proxy() as data:
            dates = data.get('date_admin', [])  # Get the list of dates from the proxy data

            for date in dates:
                async with db.execute("SELECT EXISTS(SELECT 1 FROM dates WHERE date_admin = ?)",
                                      (date,)) as cursor:
                    exists = await cursor.fetchone()

                if not exists[0]:
                    await db.execute("INSERT INTO dates (date_admin) VALUES (?)", (date,))
                    await db.commit()


async def add_item(state):
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        async with state.proxy() as data:
            await cur.execute(
                "INSERT INTO accounts (service, name, surname, date_client, phone) VALUES (?, ?, ?, ?, ?)",
                (data['service'], data['name'], data['surname'], data['date_client'], data['phone']))
        await db.commit()


async def delete_user(user_id: int) -> None:
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("DELETE FROM accounts WHERE user_id = ?", (user_id,))
        await db.commit()


async def delete_date(user_id: int) -> None:
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("DELETE FROM dates WHERE date_admin = ?", (user_id,))
        await db.commit()


async def get_admin_date():
    async with aiosqlite.connect('utils/tg.db') as db:
        cur = await db.cursor()
        await cur.execute("SELECT date_admin FROM dates")
        data = await cur.fetchall()
        return data


async def is_admin(user_id):
    async with aiosqlite.connect('utils/tg.db') as db:
        async with db.execute("SELECT user_id FROM admins WHERE user_id = ?", (user_id,)) as cursor:
            admin_data = await cursor.fetchone()

    return admin_data is not None


async def add_admin(user_id):
    if await is_admin(user_id):
        return False

    async with aiosqlite.connect('utils/tg.db') as db:
        await db.execute("INSERT INTO admins (user_id) VALUES (?)", (user_id,))
        await db.commit()

    return True


async def remove_admin(user_id):
    if not await is_admin(user_id):
        return False

    async with aiosqlite.connect('utils/tg.db') as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()

    return True
