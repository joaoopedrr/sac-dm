"""
sacpy.py — Framework unificado para análise SAC-DM/SAC-AM
==========================================================

Implementa:
  - SAC-DM (Signal Analysis based on Chaos using Density of Maxima)
  - SAC-AM (Signal Analysis based on Chaos using Amplitude of Maxima)
  - Teste 0-1 de Gottwald & Melbourne (2009)
  - Teste de determinismo simbólico de Kulp & Smith (2011)
  - Geradores de sinais caóticos sintéticos (Lorenz, Rössler, logístico)
  - Geradores de controles (periódico, ruído branco)
  - Análise de sensibilidade (SNR, comprimento de janela)

Uso como biblioteca:
    >>> import sacpy as sp
    >>> x = sp.lorenz(T=20, fs=1000)
    >>> res = sp.sac_full(x, fs=1000)
    >>> print(res.D, res.A)

Uso como demonstração gráfica:
    $ python sacpy.py
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass, field
from typing import Callable, Optional
from scipy.integrate import solve_ivp
from scipy.signal import find_peaks


# ============================================================
# 1. NÚCLEO: SAC-DM e SAC-AM
# ============================================================

@dataclass
class SACResult:
    """Resultado da aplicação de SAC-DM/SAC-AM a um sinal."""
    D: float
    A: float
    n_maxima: int
    duration: float
    peak_indices: np.ndarray = field(repr=False)


def sac_dm(x: np.ndarray, fs: float) -> float:
    """SAC-DM: densidade de máximos locais (Hz)."""
    if x.size < 3:
        return 0.0
    left = x[1:-1] > x[:-2]
    right = x[1:-1] > x[2:]
    n_max = int(np.sum(left & right))
    T = x.size / fs
    return n_max / T if T > 0 else 0.0


def sac_am(x: np.ndarray, fs: float) -> float:
    """SAC-AM: amplitude média dos máximos locais."""
    _, props = find_peaks(x)
    if props["peak_heights"].size == 0:
        return 0.0
    return float(np.mean(np.abs(props["peak_heights"])))


def sac_full(x: np.ndarray, fs: float) -> SACResult:
    """Aplica SAC-DM e SAC-AM simultaneamente."""
    peaks, _ = find_peaks(x)
    T = x.size / fs
    D = peaks.size / T if T > 0 else 0.0
    A = float(np.mean(np.abs(x[peaks]))) if peaks.size > 0 else 0.0
    return SACResult(D=D, A=A, n_maxima=int(peaks.size),
                     duration=T, peak_indices=peaks)


# ============================================================
# 2. TESTE 0-1 DE GOTTWALD-MELBOURNE
# ============================================================

def test_01(phi: np.ndarray, n_c: int = 100,
            seed: Optional[int] = 42) -> dict:
    """
    Teste 0-1 de Gottwald & Melbourne (2009) — implementação correta.

    Referência: Gottwald, G. A.; Melbourne, I. On the implementation
    of the 0-1 test for chaos. SIAM J. Appl. Dyn. Syst., v. 8, n. 1,
    p. 129-145, 2009. DOI: 10.1137/080718851.

    Retorna K médio sobre n_c valores aleatórios de c ∈ (π/5, 4π/5).
    K ≈ 0 → regular/periódico; K ≈ 1 → caótico.
    """
    phi = np.asarray(phi, dtype=float)
    N = phi.size
    if N < 100:
        return {"K_mean": 0.0, "K_median": 0.0, "K_std": 0.0,
                "K_all": np.zeros(n_c)}

    # Normalização: crucial para o teste 0-1
    phi = phi - phi.mean()
    if phi.std() > 0:
        phi = phi / phi.std()

    rng = np.random.default_rng(seed)
    n_cut = N // 10               # descarta transiente (Gottwald 2009, p.132)
    n = np.arange(1, N + 1)
    Ks = np.empty(n_c)

    for i in range(n_c):
        # c amostrado em (π/5, 4π/5) — recomendação do artigo original
        c = rng.uniform(np.pi / 5, 4 * np.pi / 5)
        p = np.cumsum(phi * np.cos(n * c))
        q = np.cumsum(phi * np.sin(n * c))

        # M_c(n) = deslocamento quadrático médio para o lag n
        # Lag n vai de 1 até N/10
        lags = np.arange(1, n_cut)
        M_c = np.empty(lags.size)
        for k, lag in enumerate(lags):
            dp = p[lag:] - p[:-lag]
            dq = q[lag:] - q[:-lag]
            M_c[k] = np.mean(dp**2 + dq**2)

        # K_c = correlação entre lags e M_c, mas usando a forma
        # robusta recomendada por Gottwald: covariância normalizada
        # (equivalente a regressão linear de M_c contra lags)
        lags_mean = lags.mean()
        M_mean = M_c.mean()
        cov = np.sum((lags - lags_mean) * (M_c - M_mean))
        var_lags = np.sum((lags - lags_mean) ** 2)
        var_M = np.sum((M_c - M_mean) ** 2)
        if var_lags == 0 or var_M == 0:
            Ks[i] = 0.0
        else:
            Ks[i] = cov / np.sqrt(var_lags * var_M)

    return {"K_mean": float(np.mean(Ks)),
            "K_median": float(np.median(Ks)),
            "K_std": float(np.std(Ks)),
            "K_all": Ks}

def _01_transforms(phi: np.ndarray, c: float) -> tuple[np.ndarray, np.ndarray]:
    """Retorna (p_c, q_c) do teste 0-1 para um dado c."""
    n = np.arange(1, phi.size + 1)
    p = np.cumsum(phi * np.cos(n * c))
    q = np.cumsum(phi * np.sin(n * c))
    return p, q


# ============================================================
# 3. TESTE DE KULP-SMITH
# ============================================================

def test_kulp_smith(x: np.ndarray, n_symbols: int = 4,
                    embedding: int = 3, delay: int = 1) -> dict:
    """Teste de determinismo para séries simbólicas ruidosas."""
    qs = np.quantile(x, np.linspace(0, 1, n_symbols + 1))
    qs[0] -= 1e-12; qs[-1] += 1e-12
    s = np.digitize(x, qs[1:-1])

    N = len(s) - (embedding - 1) * delay
    if N <= 0:
        return {"delta": 0.0, "n_states": 0}
    emb = np.array([s[i:i + embedding * delay:delay]
                    for i in range(N)])

    seen = {}
    for i in range(N - 1):
        seen.setdefault(tuple(emb[i]), []).append(tuple(emb[i + 1]))

    deterministic = sum(1 for v in seen.values() if len(set(v)) == 1)
    total = len(seen)
    delta = deterministic / total if total > 0 else 0.0
    return {"delta": delta, "n_states": total}


# ============================================================
# 4. GERADORES DE SINAIS
# ============================================================

def lorenz(T: float = 200.0, fs: float = 200.0,
           sigma: float = 10.0, rho: float = 28.0,
           beta: float = 8/3) -> np.ndarray:
    """Atrator de Lorenz. Padrão: T=200s, fs=200Hz (20000 amostras)."""
    n = int(T * fs)
    t_eval = np.linspace(0, T, n)
    sol = solve_ivp(
        lambda t, y: [sigma*(y[1]-y[0]),
                      y[0]*(rho-y[2])-y[1],
                      y[0]*y[1]-beta*y[2]],
        [0, T], [1.0, 1.0, 1.0], t_eval=t_eval,
        method="RK45", rtol=1e-8, atol=1e-10)
    return sol.y[0]


def rossler(T: float = 200.0, fs: float = 200.0,
            a: float = 0.2, b: float = 0.2,
            c: float = 5.7) -> np.ndarray:
    """Atrator de Rössler. Padrão: T=200s, fs=200Hz."""
    n = int(T * fs)
    t_eval = np.linspace(0, T, n)
    sol = solve_ivp(
        lambda t, y: [-y[1]-y[2], y[0]+a*y[1], b+y[2]*(y[0]-c)],
        [0, T], [1.0, 1.0, 1.0], t_eval=t_eval,
        method="RK45", rtol=1e-8, atol=1e-10)
    return sol.y[0]


def logistic(n: int = 20000, r: float = 3.99,
             x0: float = 0.4) -> np.ndarray:
    """Mapa logístico. 'fs=1' significa: 1 amostra por iteração."""
    x = np.empty(n); x[0] = x0
    for i in range(1, n):
        x[i] = r * x[i-1] * (1 - x[i-1])
    return x


def harmonic(f: float = 50.0, T: float = 1.0,
             fs: float = 10000.0) -> np.ndarray:
    """Sinal periódico de referência (não-caótico)."""
    t = np.linspace(0, T, int(T*fs), endpoint=False)
    return np.sin(2*np.pi*f*t)


def white_noise(n: int = 10000, seed: int = 0) -> np.ndarray:
    """Ruído branco gaussiano de referência."""
    return np.random.default_rng(seed).standard_normal(n)


def add_noise(x: np.ndarray, snr_db: float, seed: int = 0) -> np.ndarray:
    """Adiciona ruído branco com SNR especificado (dB)."""
    rng = np.random.default_rng(seed)
    p_sig = np.mean(x**2)
    p_noise = p_sig / (10**(snr_db/10))
    return x + rng.normal(0, np.sqrt(p_noise), size=x.shape)


# ============================================================
# 5. ANÁLISE DE SENSIBILIDADE
# ============================================================

def sensitivity_snr(signal_fn: Callable[[], np.ndarray], fs: float,
                    snr_range: np.ndarray = np.arange(-5, 35, 5),
                    n_trials: int = 15) -> dict:
    """SAC-DM em função da SNR."""
    D_mean, D_std = [], []
    for snr in snr_range:
        Ds = [sac_dm(add_noise(signal_fn(), snr, seed=t), fs)
              for t in range(n_trials)]
        D_mean.append(np.mean(Ds)); D_std.append(np.std(Ds))
    return {"snr": snr_range,
            "D_mean": np.array(D_mean),
            "D_std": np.array(D_std)}


def sensitivity_window(signal: np.ndarray, fs: float,
                       fractions: np.ndarray =
                       np.linspace(0.05, 1.0, 25)) -> dict:
    """SAC-DM em função do comprimento da janela."""
    N = signal.size
    D = [sac_dm(signal[:max(int(f*N), 3)], fs) for f in fractions]
    return {"fractions": fractions,
            "window_seconds": fractions * N / fs,
            "D": np.array(D)}


# ============================================================
# 6. DEMONSTRAÇÃO GRÁFICA ROBUSTA
# ============================================================

def _demo_graficos():
    """Gera um painel robusto de gráficos demonstrando o sacpy."""
    import matplotlib
    matplotlib.use("Agg")  # não abre janela; salva arquivos
    import matplotlib.pyplot as plt
    from matplotlib.gridspec import GridSpec
    from scipy.stats import gaussian_kde

    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 10,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "figure.dpi": 130,
        "savefig.bbox": "tight",
    })

    print("=" * 70)
    print(" sacpy — demonstração gráfica robusta")
    print("=" * 70)

    # -------- Geração dos sinais --------
    print("\n[1/6] Gerando sinais sintéticos...")
    fs = 200.0                    # <-- era 1000
    T = 200.0                     # <-- era 20
    x_lorenz = lorenz(T=T, fs=fs)
    x_rossler = rossler(T=T, fs=fs)
    x_logistic = logistic(n=20000, r=3.99)
    x_harm = harmonic(f=2.0, T=T, fs=fs)   # 2 Hz para visualização
    x_noise = white_noise(n=20000, seed=42)

    # -------- Métricas --------
    print("\n[2/6] Calculando SAC-DM, SAC-AM, teste 0-1 e Kulp-Smith...")
    systems = [
        ("Lorenz",     x_lorenz,   fs),
        ("Rössler",    x_rossler,  fs),
        ("Logístico",  x_logistic, 1.0),
        ("Harmônico",  x_harm,     fs),
        ("Ruído",      x_noise,    1.0),
    ]
    results = []
    for name, x, f in systems:
        r = sac_full(x, f)
        k = test_01(x, n_c=60)
        ks = test_kulp_smith(x)
        results.append({
            "name": name, "x": x, "fs": f,
            "D": r.D, "A": r.A, "peaks": r.peak_indices,
            "K": k["K_median"], "K_all": k["K_all"],
            "delta": ks["delta"],
        })
        print(f"      {name:10s} D={r.D:8.3f} Hz  A={r.A:7.3f}  "
              f"K={k['K_median']:+.3f}  δ={ks['delta']:.3f}")

    # ============================================================
    # PAINEL PRINCIPAL
    # ============================================================
    print("\n[3/6] Construindo painel principal...")
    fig = plt.figure(figsize=(18, 14))
    gs = GridSpec(4, 3, figure=fig, hspace=0.55, wspace=0.35)

    # ---- Linha 1: séries temporais ----
    colors = ["#08519c", "#cb181d", "#238b45", "#807dba", "#525252"]
    for i, (name, x, f) in enumerate(systems):
        ax = fig.add_subplot(gs[0, i]) if i < 3 else None
        if i < 3:
            n_show = min(1500, x.size)
            ax.plot(np.arange(n_show)/f, x[:n_show],
                    color=colors[i], lw=0.6)
            ax.set_title(f"{name} — série temporal")
            ax.set_xlabel("t (s)"); ax.set_ylabel("x(t)")
            ax.grid(alpha=0.25)
    # Linha 1, terceira posição: comparação de 4 sistemas
    ax_cmp = fig.add_subplot(gs[0, 2])
    for i, (name, x, f) in enumerate(systems[:3]):
        n_show = min(1000, x.size)
        ax_cmp.plot(np.arange(n_show)/f, x[:n_show],
                    color=colors[i], lw=0.5, alpha=0.8, label=name)
    ax_cmp.set_title("Comparação: 3 caóticos")
    ax_cmp.set_xlabel("t (s)"); ax_cmp.legend(fontsize=7)
    ax_cmp.grid(alpha=0.25)

    # ---- Linha 2: SAC-DM em janelas deslizantes ----
    print("      ... SAC-DM em janelas deslizantes")
    ax2 = fig.add_subplot(gs[1, :])
    win = 1000
    step = 100
    for i, (name, x, f) in enumerate(systems[:4]):
        Ds, ts = [], []
        for j in range(0, x.size - win, step):
            Ds.append(sac_dm(x[j:j+win], f))
            ts.append((j + win/2)/f)
        ax2.plot(ts, Ds, color=colors[i], lw=1.3,
                 label=f"{name} (média={np.mean(Ds):.2f} Hz)")
    ax2.set_title("SAC-DM em janelas deslizantes — separação entre regimes")
    ax2.set_xlabel("tempo (s)"); ax2.set_ylabel("SAC-DM (Hz)")
    ax2.legend(loc="upper right", fontsize=9)
    ax2.grid(alpha=0.3)

    # ---- Linha 3: teste 0-1 (histogramas de K) ----
    print("      ... histogramas do teste 0-1")
    for i, r in enumerate(results[:3]):
        ax = fig.add_subplot(gs[2, i])
        ax.hist(r["K_all"], bins=15, color=colors[i],
                edgecolor="black", alpha=0.8)
        ax.axvline(r["K"], color="red", ls="--", lw=2,
                   label=f"mediana = {r['K']:.2f}")
        ax.set_xlim(-0.2, 1.2)
        ax.set_title(f"Teste 0-1 — {r['name']}")
        ax.set_xlabel("K"); ax.set_ylabel("frequência")
        ax.legend(fontsize=8); ax.grid(alpha=0.3, axis="y")

    # ---- Linha 4: comparações ----
    # 4a: SAC-DM vs SAC-AM
    print("      ... SAC-DM vs SAC-AM")
    ax4a = fig.add_subplot(gs[3, 0])
    names = [r["name"] for r in results]
    D_vals = [r["D"] for r in results]
    ax4a.bar(names, D_vals, color=colors, edgecolor="black")
    ax4a.set_ylabel("SAC-DM (Hz)")
    ax4a.set_title("SAC-DM por sistema")
    ax4a.tick_params(axis="x", rotation=25, labelsize=8)
    ax4a.grid(alpha=0.3, axis="y")
    for i, v in enumerate(D_vals):
        ax4a.text(i, v, f"{v:.1f}", ha="center", va="bottom",
                  fontsize=8, fontweight="bold")

        # 4b: distribuição de K (boxplot)
    print("      ... boxplot de K")
    ax4b = fig.add_subplot(gs[3, 1])
    K_data = [r["K_all"] for r in results]
    try:
        bp = ax4b.boxplot(K_data, tick_labels=names, patch_artist=True)
    except TypeError:
        # Matplotlib < 3.9
        bp = ax4b.boxplot(K_data, labels=names, patch_artist=True)
    for patch, c in zip(bp["boxes"], colors):
        patch.set_facecolor(c); patch.set_alpha(0.7)
    ax4b.axhline(0.5, color="gray", ls=":", lw=1)
    ax4b.set_ylim(-0.1, 1.1)
    ax4b.set_ylabel("K")
    ax4b.set_title("Distribuição de K (teste 0-1)")
    ax4b.tick_params(axis="x", rotation=25, labelsize=8)
    ax4b.grid(alpha=0.3, axis="y")

    # 4c: SAC-DM da série completa com máximos marcados (Lorenz)
    ax4c = fig.add_subplot(gs[3, 2])
    r = results[0]
    x, fs_l = r["x"], r["fs"]
    n_show = 800
    ax4c.plot(np.arange(n_show)/fs_l, x[:n_show],
              color=colors[0], lw=0.9)
    pk = r["peaks"][r["peaks"] < n_show]
    ax4c.scatter(pk/fs_l, x[pk], color="red", s=14, zorder=5,
                 label=f"{len(pk)} máximos")
    ax4c.set_title(f"Lorenz: máximos (SAC-DM={r['D']:.1f} Hz)")
    ax4c.set_xlabel("t (s)"); ax4c.set_ylabel("x(t)")
    ax4c.legend(fontsize=8); ax4c.grid(alpha=0.25)

    fig.suptitle("sacpy — demonstração de SAC-DM, SAC-AM e testes de caos",
                 fontsize=15, fontweight="bold", y=0.995)
    fig.savefig("sacpy_dashboard.png", dpi=130)
    print("      -> sacpy_dashboard.png")
    plt.close(fig)

    # ============================================================
    # PAINEL 2: sensibilidade a SNR e ao comprimento de janela
    # ============================================================
    print("\n[4/6] Painel de sensibilidade ao ruído...")
    fig2, axes = plt.subplots(1, 3, figsize=(16, 4.5))
    snr_systems = [
        ("Lorenz", lambda: lorenz(T=10, fs=fs), fs),
        ("Logístico", lambda: logistic(n=8000, r=3.99), 1.0),
        ("Rössler", lambda: rossler(T=20, fs=fs), fs),
    ]
    for ax, (name, fn, f) in zip(axes, snr_systems):
        res = sensitivity_snr(fn, f, n_trials=10)
        ax.errorbar(res["snr"], res["D_mean"], yerr=res["D_std"],
                    marker="o", capsize=4, lw=1.6, color="#08519c")
        ax.set_xlabel("SNR (dB)"); ax.set_ylabel("SAC-DM (Hz)")
        ax.set_title(name); ax.grid(alpha=0.3)
    fig2.suptitle("Sensibilidade do SAC-DM ao ruído aditivo",
                  fontsize=14, fontweight="bold")
    fig2.tight_layout()
    fig2.savefig("sacpy_snr.png", dpi=130)
    print("      -> sacpy_snr.png")
    plt.close(fig2)

    # ============================================================
    # PAINEL 3: convergência do SAC-DM com a janela
    # ============================================================
    print("\n[5/6] Painel de convergência com comprimento de janela...")
    fig3, ax = plt.subplots(figsize=(9, 5))
    win_systems = [
        ("Lorenz", lorenz(T=30, fs=fs), fs, "#08519c"),
        ("Rössler", rossler(T=30, fs=fs), fs, "#cb181d"),
        ("Harmônico 50 Hz", harmonic(f=50, T=30, fs=fs), fs, "#238b45"),
        ("Ruído branco", white_noise(30000), 1.0, "#807dba"),
    ]
    for name, x, f, col in win_systems:
        res = sensitivity_window(x, f)
        ax.plot(res["window_seconds"], res["D"],
                marker="o", ms=4, label=name, color=col, lw=1.5)
    ax.set_xscale("log")
    ax.set_xlabel("Duração da janela (s)")
    ax.set_ylabel("SAC-DM (Hz)")
    ax.set_title("Convergência do SAC-DM com o comprimento da janela")
    ax.legend(); ax.grid(alpha=0.3, which="both")
    fig3.savefig("sacpy_window.png", dpi=130)
    print("      -> sacpy_window.png")
    plt.close(fig3)

    # ============================================================
    # PAINEL 4: teste 0-1 visual (trajetórias p_c, q_c)
    # ============================================================
    print("\n[6/6] Painel do teste 0-1 (trajetórias p_c, q_c)...")
    fig4, axes = plt.subplots(2, 2, figsize=(11, 9))
    c_fixed = 1.7
    for ax, (name, x) in zip(axes.flat,
                             [("Lorenz", x_lorenz),
                              ("Logístico", x_logistic),
                              ("Harmônico", x_harm),
                              ("Ruído", x_noise)]):
        p, q = _01_transforms(x, c_fixed)
        # subamostra para plotar
        idx = np.linspace(0, p.size - 1, min(3000, p.size)).astype(int)
        ax.plot(p[idx], q[idx], color="#08519c", lw=0.5, alpha=0.7)
        ax.set_title(f"{name} — (p_c, q_c) com c={c_fixed}")
        ax.set_xlabel("p_c"); ax.set_ylabel("q_c")
        ax.grid(alpha=0.25)
    fig4.suptitle("Teste 0-1: trajetória (p_c, q_c) — "
                  "difusão = caos, confinamento = regular",
                  fontsize=13, fontweight="bold")
    fig4.tight_layout()
    fig4.savefig("sacpy_test01.png", dpi=130)
    print("      -> sacpy_test01.png")
    plt.close(fig4)

    print("\n" + "=" * 70)
    print(" Concluído. Arquivos gerados:")
    print("   - sacpy_dashboard.png  (painel principal, 4x3)")
    print("   - sacpy_snr.png        (sensibilidade ao ruído)")
    print("   - sacpy_window.png     (convergência com a janela)")
    print("   - sacpy_test01.png     (trajetórias do teste 0-1)")
    print("=" * 70)


# ============================================================
# 7. ENTRY POINT
# ============================================================

if __name__ == "__main__":
    _demo_graficos()