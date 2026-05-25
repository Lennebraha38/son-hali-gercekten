<?php
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }

function logMsg(string $lvl, string $msg): void {
    error_log(date('Y-m-d H:i:s') . " [$lvl] $msg");
}



define('DB_HOST', '');  // ← cPanel'den kopyala
define('DB_NAME', ''); // ← cPanel'den kopyala
define('DB_USER', '');            // ← cPanel'den kopyala
define('DB_PASS', '');           // ← kendi şifren


function getDB(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    try {
        $pdo = new PDO(
            'mysql:host=' . DB_HOST . ';dbname=' . DB_NAME . ';charset=utf8mb4',
            DB_USER, DB_PASS,
            [
                PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::MYSQL_ATTR_INIT_COMMAND => "SET NAMES utf8mb4",
            ]
        );
        logMsg('INFO', 'MySQL bağlantısı başarılı.');
    } catch (PDOException $e) {
        logMsg('ERROR', 'DB hatası: ' . $e->getMessage());
        jsonError('Veritabanı bağlantısı kurulamadı.', 500);
    }
    return $pdo;
}


function createTables(): void {
    $pdo = getDB();
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS kullanicilar (
            id     INT AUTO_INCREMENT PRIMARY KEY,
            isim   VARCHAR(80)  NOT NULL,
            eposta VARCHAR(120) NOT NULL UNIQUE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS ilanlar (
            id          INT AUTO_INCREMENT PRIMARY KEY,
            baslik      VARCHAR(255) NOT NULL,
            aciklama    TEXT,
            kategori    VARCHAR(50),
            sehir       VARCHAR(100),
            etiketler   VARCHAR(255),
            kisi        VARCHAR(50),
            tip         VARCHAR(50),
            kullanici_id INT,
            olusturulma TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ");
}


function jsonResponse(mixed $data, int $code = 200): never {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}
function jsonError(string $msg, int $code = 400): never {
    jsonResponse(['hata' => $msg], $code);
}
function getJson(): array {
    return json_decode(file_get_contents('php://input'), true) ?? [];
}


createTables();

$method   = $_SERVER['REQUEST_METHOD'];
$uri      = $_SERVER['REQUEST_URI'];
$endpoint = '/' . trim(preg_replace('#^.*?api\.php#', '', parse_url($uri, PHP_URL_PATH)), '/');
if ($endpoint === '/') $endpoint = '/';

logMsg('INFO', "[$method] $endpoint");

match(true) {
    $method === 'GET'  && $endpoint === '/'
        => jsonResponse(['durum' => 'basarili', 'mesaj' => 'Lennebraha38 API Aktif (MySQL)', 'versiyon' => '2.0']),

    $method === 'GET'  && $endpoint === '/kullanicilar'
        => kullanicilariListele(),

    $method === 'POST' && $endpoint === '/kullanici-ekle'
        => kullaniciEkle(),

    $method === 'GET'  && $endpoint === '/ilanlar'
        => ilanlariListele(),

    $method === 'POST' && $endpoint === '/ilan-ekle'
        => ilanEkle(),

    preg_match('#^/kullanici/(\d+)$#', $endpoint, $m) && $method === 'DELETE'
        => kullaniciSil((int)$m[1]),

    default => jsonError("Endpoint bulunamadı: $endpoint", 404),
};


function kullanicilariListele(): never {
    $rows = getDB()->query('SELECT id, isim, eposta FROM kullanicilar ORDER BY id DESC')->fetchAll();
    jsonResponse(['durum' => 'basarili', 'kullanicilar' => $rows, 'toplam' => count($rows)]);
}

function kullaniciEkle(): never {
    $v = getJson();
    if (empty($v['isim']) || empty($v['eposta'])) jsonError('isim ve eposta zorunludur.', 400);
    if (!filter_var($v['eposta'], FILTER_VALIDATE_EMAIL)) jsonError('Geçersiz e-posta.', 400);

    try {
        $st = getDB()->prepare('INSERT INTO kullanicilar (isim, eposta) VALUES (?, ?)');
        $st->execute([trim($v['isim']), trim($v['eposta'])]);
        $id = (int) getDB()->lastInsertId();
        jsonResponse(['durum' => 'basarili', 'kullanici' => ['id' => $id, 'isim' => $v['isim'], 'eposta' => $v['eposta']]], 201);
    } catch (PDOException $e) {
        if ($e->getCode() == 23000) jsonError('Bu e-posta zaten kayıtlı.', 409);
        jsonError('Veritabanı hatası.', 500);
    }
}

function kullaniciSil(int $id): never {
    $st = getDB()->prepare('DELETE FROM kullanicilar WHERE id = ?');
    $st->execute([$id]);
    if ($st->rowCount() === 0) jsonError("ID $id bulunamadı.", 404);
    jsonResponse(['durum' => 'basarili', 'mesaj' => "Kullanıcı ID $id silindi."]);
}

function ilanlariListele(): never {
    $rows = getDB()->query('SELECT * FROM ilanlar ORDER BY olusturulma DESC')->fetchAll();
    jsonResponse(['durum' => 'basarili', 'ilanlar' => $rows, 'toplam' => count($rows)]);
}

function ilanEkle(): never {
    $v = getJson();
    if (empty($v['baslik']) || empty($v['aciklama'])) jsonError('baslik ve aciklama zorunludur.', 400);
    try {
        $st = getDB()->prepare("INSERT INTO ilanlar (baslik, aciklama, kategori, sehir, etiketler, kisi, tip, kullanici_id)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
        $st->execute([
            trim($v['baslik']), trim($v['aciklama']),
            $v['kategori'] ?? null, $v['sehir'] ?? null,
            $v['etiketler'] ?? null, $v['kisi'] ?? '1 Kişi',
            $v['tip'] ?? 'takim', $v['kullanici_id'] ?? null,
        ]);
        $id = (int) getDB()->lastInsertId();
        jsonResponse(['durum' => 'basarili', 'ilan' => ['id' => $id] + $v], 201);
    } catch (PDOException $e) {
        logMsg('ERROR', $e->getMessage());
        jsonError('Veritabanı hatası.', 500);
    }
}