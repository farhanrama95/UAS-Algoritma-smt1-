import sys
from abc import ABC, abstractmethod



# ABSTRACTION — Abstract base class untuk tampilan tabel
class TabelBase(ABC):
    """Abstract class yang mendefinisikan kontrak tampilan tabel."""

    LEBAR = 65

    def cetak_header(self):
        print("\n" + "=" * self.LEBAR)
        print(f"{'ID':^8} | {'Nama Pelanggan':^15} | {'Berat':^10} | {'Status':^10} | {'Total':^10}")
        print("-" * self.LEBAR)

    def cetak_footer(self):
        print("=" * self.LEBAR)

    @abstractmethod
    def tampilkan(self, data: dict):
        """Subclass wajib mengimplementasikan cara tampilkan data."""
        pass

    def _cetak_baris(self, id_: str, info: dict):
        print(f"{id_:<8} | {info['Nama']:^15} | {info['Berat']:<7} kg | {info['Status']:^10} | Rp{info['Total']},-")



# INHERITANCE + POLYMORPHISM — Dua varian tabel
class TabelNormal(TabelBase):
    """Menampilkan data sesuai urutan masuk (insertion order)."""

    def tampilkan(self, data: dict):
        self.cetak_header()
        if not data:
            print(f"{'DATA TIDAK DITEMUKAN':^{self.LEBAR}}")
        else:
            for id_, info in data.items():
                self._cetak_baris(id_, info)
        self.cetak_footer()


class TabelSortingID(TabelBase):
    """Menampilkan data diurutkan berdasarkan ID (ascending / descending)."""

    def __init__(self, reverse: bool = False):
        self._reverse = reverse  # ENCAPSULATION: atribut private

    def tampilkan(self, data: dict):
        self.cetak_header()
        if not data:
            print(f"{'DATA TIDAK DITEMUKAN':^{self.LEBAR}}")
        else:
            for id_ in sorted(data.keys(), reverse=self._reverse):
                self._cetak_baris(id_, data[id_])
        self.cetak_footer()



# ENCAPSULATION — Model data satu pelanggan
class Pelanggan:
    """Menyimpan dan mengelola data satu transaksi pelanggan."""

    HARGA_PER_KG = 8_500

    def __init__(self, nama: str, berat: int):
        self._nama   = nama           # private
        self._berat  = berat          # private
        self._status = "Proses"       # private, default
        self._total  = berat * self.HARGA_PER_KG

    # --- Getter ---
    @property
    def nama(self):   return self._nama
    @property
    def berat(self):  return self._berat
    @property
    def status(self): return self._status
    @property
    def total(self):  return self._total

    # --- Setter dengan validasi ---
    @status.setter
    def status(self, nilai: str):
        if nilai not in ("Proses", "Selesai"):
            raise ValueError("Status hanya boleh 'Proses' atau 'Selesai'.")
        self._status = nilai

    def ke_dict(self) -> dict:
        """Konversi ke format dict untuk kompatibilitas tampilan tabel."""
        return {
            "Nama":   self._nama,
            "Berat":  self._berat,
            "Status": self._status,
            "Total":  self._total,
        }


# ENCAPSULATION — Manajemen keseluruhan data laundry
class ManajemenLaundry:
    """Mengelola koleksi Pelanggan dan semua operasi CRUD."""

    def __init__(self):
        self._data: dict[str, Pelanggan] = {}  # private storage
        self._tabel_normal = TabelNormal()      # dependency injection

    # ---- helpers internal ----
    def _ada(self, id_: str) -> bool:
        return id_ in self._data

    def _ke_dict_semua(self) -> dict:
        return {id_: p.ke_dict() for id_, p in self._data.items()}

    # ---- operasi publik ----
    def tambah(self, id_: str, nama: str, berat: int):
        id_ = id_.upper()
        if self._ada(id_):
            print("❌  ID sudah digunakan!")
            return
        self._data[id_] = Pelanggan(nama, berat)
        print("✅  Data berhasil ditambahkan!")

    def tampilkan_semua(self):
        self._tabel_normal.tampilkan(self._ke_dict_semua())

    def edit_status(self, id_: str, status_baru: str):
        id_ = id_.upper()
        if not self._ada(id_):
            print("❌  ID tidak ditemukan.")
            return
        try:
            self._data[id_].status = status_baru.capitalize()
            print("✅  Status berhasil diubah.")
        except ValueError as e:
            print(f"❌  {e}")

    def hapus(self, id_: str):
        id_ = id_.upper()
        if not self._ada(id_):
            print("❌  ID tidak ditemukan.")
            return
        del self._data[id_]
        print("✅  Data berhasil dihapus!")

    def cari(self, cari_id: str):
        """Binary search berdasarkan ID."""
        if not self._data:
            print("Data kosong, tidak ada yang bisa dicari.")
            return
        cari_id    = cari_id.upper()
        daftar_id  = sorted(self._data.keys())
        low, high  = 0, len(daftar_id) - 1
        found      = False

        while low <= high:
            mid = (low + high) // 2
            if daftar_id[mid] == cari_id:
                found = True
                break
            elif daftar_id[mid] < cari_id:
                low = mid + 1
            else:
                high = mid - 1

        if found:
            print(f"\n[Data Ditemukan pada indeks ke-{mid}]")
            self._tabel_normal.tampilkan({cari_id: self._data[cari_id].ke_dict()})
        else:
            print(f"ID '{cari_id}' tidak ditemukan dalam sistem.")

    def urutkan(self, reverse: bool = False):
        tabel = TabelSortingID(reverse=reverse)
        tabel.tampilkan(self._ke_dict_semua())



# ABSTRACTION — Abstract base class untuk menu
class MenuBase(ABC):
    """Kontrak untuk semua menu interaktif."""

    @abstractmethod
    def tampilkan_opsi(self):
        pass

    @abstractmethod
    def proses(self, pilihan: str, laundry: ManajemenLaundry):
        pass

    def jalankan(self, laundry: ManajemenLaundry):
        while True:
            self.tampilkan_opsi()
            pilihan = input("Silakan pilih menu [0-6]: ").strip()
            if not self.proses(pilihan, laundry):
                break  # sinyal keluar



# INHERITANCE — Implementasi menu utama
class MenuUtama(MenuBase):
    """Menu utama aplikasi laundry."""

    def tampilkan_opsi(self):
        print("\n---------| MENU |---------")
        print("1. Input data")
        print("2. Tampilkan data")
        print("3. Edit status")
        print("4. Hapus data")
        print("5. Cari data")
        print("6. Urutkan data")
        print("0. Keluar")

    def proses(self, pilihan: str, laundry: ManajemenLaundry) -> bool:
        """Mengembalikan False jika pengguna memilih keluar."""
        match pilihan:
            case "1":
                self._input_data(laundry)
            case "2":
                laundry.tampilkan_semua()
            case "3":
                self._edit_status(laundry)
            case "4":
                self._hapus_data(laundry)
            case "5":
                self._cari_data(laundry)
            case "6":
                self._urutkan_data(laundry)
            case "0":
                print("Sistem keluar. Terima kasih!")
                sys.exit()
            case _:
                print("❌  Pilihan tidak valid.")
        return True

    # ---- sub-handler private ----
    def _input_data(self, laundry: ManajemenLaundry):
        print("\n--- Input Transaksi Baru ---")
        id_baru = input("Buat ID (cth: ID001): ")
        nama    = input("Masukkan nama       : ")
        berat   = int(input("Masukkan berat cucian (kg): "))
        laundry.tambah(id_baru, nama, berat)

    def _edit_status(self, laundry: ManajemenLaundry):
        id_edit     = input("Masukkan ID yang ingin diedit statusnya: ")
        status_baru = input("Masukkan status baru (Proses/Selesai)  : ")
        laundry.edit_status(id_edit, status_baru)

    def _hapus_data(self, laundry: ManajemenLaundry):
        id_hapus = input("Masukkan ID yang akan dihapus: ")
        laundry.hapus(id_hapus)

    def _cari_data(self, laundry: ManajemenLaundry):
        print("\n--- Cari ID Pelanggan ---")
        cari_id = input("Masukkan ID yang dicari (cth: ID001): ")
        laundry.cari(cari_id)

    def _urutkan_data(self, laundry: ManajemenLaundry):
        print("\n--- Urutkan Data Berdasarkan ID ---")
        print("1. Ascending  (A → Z)")
        print("2. Descending (Z → A)")
        arah = input("Pilih urutan (1/2): ")
        if arah == "1":
            laundry.urutkan(reverse=False)
        elif arah == "2":
            laundry.urutkan(reverse=True)
        else:
            print("❌  Pilihan tidak valid!")


# Entry point

if __name__ == "__main__":
    laundry = ManajemenLaundry()
    menu    = MenuUtama()
    menu.jalankan(laundry)