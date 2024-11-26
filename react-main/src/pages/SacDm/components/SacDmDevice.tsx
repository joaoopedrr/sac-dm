import Chart from "react-apexcharts";
import { SacDmProps } from "../../SacDm/types";
import { EmptyData } from "../../../components/EmptyData";
import React, { useCallback, useEffect, useState } from "react";
import { SacDmDefaultProps } from "../../../types";
import sacDmDefault from "../../../app/services/sacdm_default";
import styled from "styled-components";

const Divider = styled.hr`
  border: none;
  border-top: 2px solid ${({ theme }) => theme.gray800};
  margin: 20px 0;
`;

const Section = styled.div`
  margin-bottom: 40px;
`;

export const SacDmDevice = ({
  deviceId,
  sacDm,
}: {
  deviceId: number ;
  sacDm: SacDmProps[];
}) => {
  const [sacDmMean, setsacDmMean] = useState<SacDmDefaultProps>();

  const loadSacDmDefault = useCallback(async () => {
    try {
      const response = await sacDmDefault.getSacDmDefault(deviceId);
      setsacDmMean(response);
      
      // TODO: Alterar para pegar o veículo selecionado
    } catch (error) {
      console.error(error);
    }
  }, []);

  useEffect(() => {
    loadSacDmDefault();
  }, [loadSacDmDefault]);

  if (!deviceId) {
    return null;
  }

  // TODO fazer a leitura correta dos dados do status
  // Função para verificar o status dos dados com base em sacDmMean.status
  const checkDataStatus = () => {
    //return sacDmMean?.status === "Ok" ? "Ok" : "Falha";
    return "Ok"
  };

  const optionsChart = {
    chart: {
      id: "device-metrics",
    },
    xaxis: {
      categories: sacDm.map((item: SacDmProps) => item.timestamp),
      labels: {
        show: false,
      },
    },
    yaxis: {
      labels: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
        style: {
          colors: ["#E0E0E0"],
        },
      },
    },
    tooltip: {
      theme: "dark",
      y: {
        formatter: (value: number) => (value ? value.toFixed(8) : "0.00000000"),
      },
    },
    legend: {
      labels: {
        colors: ["E0E0E0", "E0E0E0", "E0E0E0", "E0E0E0"],
      },
    },
  };

  const getChartData = (axis: "x" | "y" | "z") => {
    const valores = sacDm.map((item) =>
      parseFloat(item[`${axis}_value`].toFixed(8))
    );
    const medias = Array(sacDm.length).fill(sacDmMean?.[`${axis}_mean`] ?? 0);
    const desvioPadraoSuperior = sacDmMean
      ? Array(sacDm.length).fill(
          sacDmMean[`${axis}_mean`] + sacDmMean[`${axis}_standard_deviation`]
        )
      : [];
    const desvioPadraoInferior = sacDmMean
      ? Array(sacDm.length).fill(
          sacDmMean[`${axis}_mean`] - sacDmMean[`${axis}_standard_deviation`]
        )
      : [];

    return [
      { name: "Valor", data: valores },
      { name: "Média", data: medias },
      { name: "Desvio Padrão Superior", data: desvioPadraoSuperior },
      { name: "Desvio Padrão Inferior", data: desvioPadraoInferior },
    ];
  };

  const dataX = getChartData("x");
  const dataY = getChartData("y");
  const dataZ = getChartData("z");

  return (
    <div style={{ zIndex: 0, position: "relative" }}>
      {/* Retângulo com status de dados */}
      <div
        style={{
          backgroundColor: checkDataStatus() === "Ok" ? "#4CAF50" : "#F44336",
          color: "white",
          padding: "10px",
          textAlign: "center",
          borderRadius: "5px",
          marginBottom: "15px",
        }}
      >
        {checkDataStatus()}
      </div>

      {/* Gráficos para os eixos X, Y e Z */}
      <Section>
        <h3>Eixo X</h3>
        <Chart options={optionsChart} series={dataX} type="line" height="350" />
        <Divider />
      </Section>

      <Section>
        <h3>Eixo Y</h3>
        <Chart options={optionsChart} series={dataY} type="line" height="350" />
        <Divider />
      </Section>

      <Section>
        <h3>Eixo Z</h3>
        <Chart options={optionsChart} series={dataZ} type="line" height="350" />
        <Divider />
      </Section>

      {sacDm.length === 0 && (
        <EmptyData message="Nenhum dado encontrado para o dispositivo selecionado" />
      )}
    </div>
  );
};

export default React.memo(SacDmDevice, (prevProps, nextProps) => {
  return (
    prevProps.deviceId === nextProps.deviceId &&
    JSON.stringify(prevProps.sacDm) === JSON.stringify(nextProps.sacDm)
  );
});
